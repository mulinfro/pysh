
import shutil
import os
from libs.utils import normal_leven
import subprocess

__all__ =  ['pwd', 'isFile', 'isDir', 'ls', 'll', 'read',
            'mkdir', 'rm', 'cp', 'mv', 'find', 'doc', 'osCall', 'dirMap', 'dirsMap', 'CDHIST']

def pwd():
    """
        pwd()
        Current work directory
    """
    return os.getcwd()

def read(files, p="rb"):
    """ 
        read(files: string| List[string], p="rb")
        files: file name or list of files;   p: read mode

        return: Lazyed!! lines
        example:
            read("file1.txt", "r")
            read(["file1.txt", "file2.txt", "file3.txt"], "r")
    """
    if type(files) == str: files = [files]
    for path in files:
        pathes = replace_if_star_dir(path)
        for file_name in pathes:
            if isDir(file_name): continue
            f = open(file_name, p)
            yield f.read()
            f.close()
    
def doc(obj):
    """
        return python object's __doc__
    """
    print(obj.__doc__)

def path_expand(path):
    path = path.strip()
    if path.startswith("~"):
        return os.path.expanduser("~") + path[1:]
    return path

def isFile(filename):
    """
        isFile(filename: string)
        determine whether a path is a file
    """
    return os.path.isfile(filename)

def isDir(path):
    """
        isDir(filename: string)
        determine whether a path is a directory
    """
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

HOME_DIR = os.path.expanduser("~")
CDHIST = [("~", os.getcwd() )]

def cd(path = ".."):
    """
        cd(path = ".." : int | string)
        cd: change working directory
        two mode:
            int -> hitory cd path in cdh;
            string -> cd to this path
    """ 

    def _cd_helper():
        #config.cdh.clear()
        #config.cdh.extend([  (x[0], i) for i, x in enumerate(CDHIST) ])
        os.chdir(CDHIST[0][1])

    if type(path) == int:
        cd_path = CDHIST.pop(path)
        CDHIST.insert(0, cd_path)
        _cd_helper()
        return

    path_expand(path)
    if not os.path.isdir(path):
        print("Error Not_a_dir: %s" % path )
        return
    abspath = os.path.abspath(path)
    CDHIST.insert(0, (path, abspath))
    # LRU
    for i in range(1, len(CDHIST)):
        if CDHIST[i][0] == CDHIST[0][0]:
            CDHIST.pop(i)
            break
    if len(CDHIST) > 20: CDHIST.pop(-1)
    _cd_helper()


def ls(path=".", p=""):
    """
       ls(path=".", p="")
           list all files or directories in "path"
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

def dirMap(func, dir_path, p="f"):
    """
        dirMap(func: function, dirpath: string, p="f" )
            apply "func" in all files or directories

           p = [r,d,f]
           r: recursive ls sub dir
           f: return only files
           d: return only directories

       return:
           [func(f1), func(f2), ..]
    """
    ans = []
    for f in ls(dir_path, p):
        val = func(f)
        if val is not None:
            ans.append(val)
    return ans

def dirsMap(func, dirs_path, p="f"):
    """
        dirsMap(func: function, dirspath: iterable[string], p="f" )
          given list of dirpath, apply func to all files in all dirs
          for dir in dirspath:
              dirMap(func, dir, p)

           p = [r,d,f]
           r: recursive ls sub dir
           f: return only files
           d: return only directories
    """
    ans = []
    for dir_path in dirs_path:
        for f in ls(dir_path, p):
            val = func(dir_path, f)
            if val is not None:
                ans.append(val)
    return ans

class os_return_obj:
    def __init__(self, stdout, returncode):
        self.stdout = stdout if stdout else ""
        self.returncode = returncode

    def __str__(self):
        if self.returncode == 0:
            return self.stdout
        else:
            return "shell error code %d\n"%self.returncode

def osCall(sh):
    """
        osCall(sh: string)
        run a bash command
    """
    out_bytes = subprocess.run(sh, shell=True, stderr=subprocess.STDOUT)
    return os_return_obj(out_bytes.stdout, out_bytes.returncode)

def ll(path):
    """
        same: linux ls -al
    """
    osCall("ls -al %s"%path)

def mkdir(path, mode=0o777, p=""):
    """
       mkdir(path, mode=0o777, p="")
       mode:  permission default 0777
       p = [r]  r recursive mkdir
    """
    path = path_expand(path) 
    if "r" in p:
        os.makedirs(path, mode);
    else:
        os.mkdir(path, mode)

def rm(fpath, p=""):
    """
       remove(fpath: string, dst: string, p="")
       remove a file or directory

       p = [r]  remove directory
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
    """
       cp(src: string, dst: string, p="")
       copy a file or directory to target path
       p = [r]  
       r recursively copy
    """
    if "r" in p and isDir(src):
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
    """
       mv(src: string, dst: string, p="")
       move a file or directory to target path
       p = [r]
       r: move directory recursively
    """
    if "r" not in p:
        shutil.move(src, dst)
    else:
        mv_directory(src, dst)

def find(name, dir_path="." , p="r"):
    """
        find(name: string, dirpath="." , p="r")
        name: the name to find 
        dirpath: find in this directory
        p = r    recursive find sub dirs
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
