
import shutil
import os
from sh.utils import normal_leven

__all__ =  ['pwd', 'is_file', 'is_dir', 'replace_if_star_dir', 'ls', 'll', 
            'mkdir', 'rm', 'cp', 'mv', 'find', 'doc']

def pwd():
    """Current work directory"""
    return os.getcwd()
    
def doc(obj):
    """return python object's __doc__"""
    print(obj.__doc__)

def path_expand(path):
    if path.startswith("~"):
        return os.path.expanduser("~") + path[1:]
    return path

def is_file(filename):
    return os.path.isfile(filename)

def is_dir(path):
    return os.path.isdir(path)

def replace_if_star_dir(path):
    path = path.strip()
    if path == "*": path = "./*"
    if path[-1] == "*":
        ans = []
        path = path[0:-1]
        for filename in os.listdir(path):
            ans.append(os.path.join(path,filename))
        return ans
    return [path]

def ls(path=".", p=""):
    """shell: ls 
       p = [r,d,f]
       r: recursive ls sub dir
       f: return only files
       d: return only directories
    """
    p = p.lower()
    if "f" not in p and "d" not in p:
        p = p + "df"
    ans = []
    path = path_expand(path) 
    for filename in os.listdir(path):
        new_path = os.path.join(path,filename)
        if os.path.isdir(new_path):
            if "d" in p: ans.append(filename + "/")
            if "r" in p: 
                t = ls(new_path, p)
                t_cpl = [ os.path.join(filename, e) for e in t ]
                ans.extend(t_cpl)
        elif "f" in p:
            ans.append(filename)
    return ans

def ll():
    pass

def mkdir(path, mode=0o777, p=""):
    """shell: mkdir
       mode:  permission default 0777
       p = [r]  r recursive mkdir
    """
    path = path_expand(path) 
    if "r" in p:
        os.makedirs(path, mode);
    else:
        os.mkdir(path, mode)

def rm(fpath, p=""):
    """shell: rm
       p = [r]  
       r recursive remove
    """
    fpath = path_expand(fpath) 
    if len(fpath) < 2: return
    if "r" not in p:
        os.remove(fpath)
    else:
        shutil.rmtree(fpath)

def cptree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def cp(src, dst, p=""):
    """shell: cp
       p = [r]  
       r recursive cp
    """
    if "r" in p and is_dir(src):
        cptree(src, dst)
    else:
        shutil.copy2(src, dst)

def mv_directory(src, dst):
    flag = False
    for src_dir, dirs, files in os.walk(src):
        if not flag: 
            flag = True
            src_sys = src_dir
        dst_dir = src_dir.replace(src_sys, dst, 1)
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)

def mv(src, dst, p=""):
    """shell: mv
       p = [r]
       r: move directory recursively
    """
    if "r" not in p:
        shutil.move(src, dst)
    else:
        mv_directory(src, dst)

def find(name, dir_path="." , p="r"):
    """shell: find
       name: to find name
       dir_path: find in this directory
       p = [r]  recursive find sub dirs
    """
    files = ls(dir_path, p)
    ans = []
    for fn in files:
        head, tail = os.path.split(fn)
        dis = normal_leven(tail, name)
        ans.append((dis, fn))
    ans.sort()
    ans = ans[0:5]
    if len(ans) > 0 and ans[0][0] == 0:
        return [ans[0][1]]
    return list(map(lambda x:x[1], ans))
