def change_nested_list_value(nested_list, indices, new_value):
    # 创建一个当前列表的引用，初始指向最外层的列表
    current_level = nested_list
    
    # 遍历索引列表，直到倒数第二个索引
    for index in indices[:-1]:
        current_level = current_level[index]
    
    # 将最后一个索引位置的值设置为新值
    current_level[indices[-1]] = new_value
 
# 示例用法
nested_list = [[1, 2, [3, 4]], [5, 6], [7, [8, 9]]]
indices = [0, 2, 1]  # 想要改变的值的位置索引
new_value = 42  # 想要设置的新值
 
change_nested_list_value(nested_list, indices, new_value)
 
# 打印结果查看是否修改成功
print(nested_list)