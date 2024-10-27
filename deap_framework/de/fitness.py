import numpy as np
from sklearn.metrics import accuracy_score


def get_indices(xi):
    xi = np.round(xi)  # 数据范围在0-1之间，转化成int的同时会舍去小数部分，从而将个体映射到0-1编码
    indices = np.where(xi == 1)  # 1代表选择该实例，返回值是tuple，tuple[0]取元组中的第一个元素
    return indices[0]


def get_classes_indexes_counts(y):
    # 统计每个类别的个数，y.max()+1是类别的个数
    num_class = y.max() + 1
    counts = np.zeros(num_class, dtype=int)
    classes = []
    for i in range(y.shape[0]):  # y.shape[0]相当于y的长度
        counts[y[i]] += 1
    for i in range(num_class):
        # np.where() 返回值是一个tuple数组，np.where(y == i)[0],表示取出该tuple数组的第一个元素，是一个ndarray数组
        classes.append(np.where(y == i)[0])
    return classes, counts


def get_sub_dataset(xi, indices, x, y, classes, minimum):
    # 根据索引得到实例子集
    num_class = len(classes)
    x_sub = x[indices, :]
    y_sub = y[indices]

    # 计算实例子集各个类别的数量
    counts_sub = np.zeros(num_class, dtype=int)
    for i in range(y_sub.shape[0]):
        counts_sub[y_sub[i]] += 1
    # 遍历子集中各个类别的数量，保证大于最小数量
    for i in range(num_class):
        # 当实例个数小于minimum，随机添加实例达到最小限制
        if counts_sub[i] < minimum:
            # 转换成集合进行差运算（& | -，分别是交、并、差） unselected_indices是一个set集合
            unselected_indices_set = set(classes[i]) - set(indices)
            # list(unselected_indices)将集合转换成list
            unselected_indices = np.array(list(unselected_indices_set))
            # replace=False表示不允许重复
            random_selecte_indices = np.random.choice(unselected_indices, size=minimum - counts_sub[i], replace=False)
            # 添加后更改个体xi的参数
            for j in range(0, minimum - counts_sub[i]):  # 小于minimum，添加实例时，需要同步更改xi个体的实值大小，由小于0.5，改为大于0.5
                xi[random_selecte_indices[j]] = np.random.uniform(0.5, 1)  # 生成0.5-1的随机数
                index = np.searchsorted(indices, random_selecte_indices[j])
                indices = np.insert(indices, index, random_selecte_indices[j])
                x_sub = np.insert(x_sub, index, x[random_selecte_indices[j], :], axis=0)
                y_sub = np.insert(y_sub, index, y[random_selecte_indices[j]])
    return x_sub, y_sub, xi


# 适应度函数/目标函数
def objective_function(xi, x_train, y_train, x_test, y_test, model):  # xi表示种群的个体
    # 先将x的实值编码四舍五入得到0-1编码，根据编码得到训练子集
    indices = get_indices(xi)
    classes, counts = get_classes_indexes_counts(y_train)
    minimum = counts.min() // 2
    x_sub, y_sub, xi = get_sub_dataset(xi, indices, x_train, y_train, classes, minimum)

    # 模型训练
    model.fit(x_sub, y_sub)
    y_pred = model.predict(x_test)

    # 计算准确率
    accuracy = accuracy_score(y_test, y_pred)

    # 计算错误率
    error_rate = 1 - accuracy
    return error_rate


# 求适应度
def fitness(x, model, x_train, y_train, x_test, y_test, minimum):  # x表示种群
    result = np.empty(x.shape[0])  # 记录种群中个体的适应度
    # 计算每个个体的适应度
    for i in range(0, x.shape[0]):
        result[i] = objective_function(x[i, :], x_train, y_train, x_test, y_test, model, minimum)
    return result
