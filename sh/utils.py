
def wget():
    pass

def pipe_itertool(func, n):
    def wrapper(*args, **kw):
        for line in args[n]:
            new_args = args[0:n] + (line, ) + args[n+1:]
            ans = func(*new_args, **kw)
            if ans is not None: yield ans
    return wrapper

def unlazyed(func):
    def wrapper(*args, **kw):
        return list(func(*args, **kw))
    return wrapper

# 编辑距离； 供find匹配
def normal_leven(str1, str2):
      len_str1 = len(str1) + 1
      len_str2 = len(str2) + 1
      #create matrix
      matrix = [0 for n in range(len_str1 * len_str2)]
      #init x axis
      for i in range(len_str1):
          matrix[i] = i
      #init y axis
      for j in range(0, len(matrix), len_str1):
          if j % len_str1 == 0:
              matrix[j] = j // len_str1
          
      for i in range(1, len_str1):
          for j in range(1, len_str2):
              if str1[i-1] == str2[j-1]:
                  cost = 0
              else:
                  cost = 1
              matrix[j*len_str1+i] = min(matrix[(j-1)*len_str1+i]+1,
                                          matrix[j*len_str1+(i-1)]+1,
                                          matrix[(j-1)*len_str1+(i-1)] + cost)
          
      return matrix[-1]


if __name__ == "__main__":
    s1 = "123"
    print(normal_leven(s1,s1 ))
    s2 = s1 + "45"
    print(normal_leven(s1,s2 ))
    print(normal_leven(s2,s1 ))
    s3 = "132"
    print(normal_leven(s1,s3 ))
