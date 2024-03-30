def sum_x_to_y(n, cnt):
    if (cnt == 1):
        return n
    return (n + (n + cnt - 1)) * cnt / 2

def get_rank_list(lst):
    result = []
    l = sorted(lst)
    mp = dict()
    for i in range(0, len(lst)):
        if (lst[i] in mp.keys()):
            mp[lst[i]] += 1
        else:
            mp[lst[i]] = 1
    for i in range(0, len(lst)):
        index = l.index(lst[i]) + 1
        cnt = mp[l[index - 1]]
        result.append(sum_x_to_y(index, cnt) / cnt)
    return result


        

a = [4, 18, 9, 10, -1, 9, 25, 18, 9]
l = get_rank_list(a)
print(l)