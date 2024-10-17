import random
import pickle as pkl
import sys

def generate_neg_sample(in_file, out_file):
    item_list = []  # 用于存储所有物品ID的列表
    user_map = {}   # 用于存储每个用户的行为记录

    # 注释：数据格式为 UserID,ItemID,CategoryID,BehaviorType,Timestamp

    fi = open(in_file, "r")
    for line in fi:
        item = line.strip().split(',')  # 将每行数据按逗号分割
        if item[0] not in user_map:
            user_map[item[0]] = []  # 如果用户不在 user_map 中，则初始化一个空列表
        # 将用户的行为记录（包括时间戳）添加到 user_map 中
        user_map[item[0]].append(("\t".join(item), float(item[-1])))
        item_list.append(item[1])  # 将物品ID添加到 item_list 中

    fi = open(in_file, 'r')
    meta_map = {}  # 用于存储物品与类别的映射关系
    for line in fi:
        arr = line.strip().split(",")
        if arr[1] not in meta_map:
            meta_map[arr[1]] = arr[2]  # 将物品ID和类别ID的映射存储到 meta_map 中

    fo = open(out_file, "w")
    for key in user_map:
        # 对每个用户的行为记录按时间戳排序
        sorted_user_bh = sorted(user_map[key], key=lambda x: x[1])
        for line, t in sorted_user_bh:
            items = line.split("\t")  # 将行为记录按制表符分割
            asin = items[1]  # 获取当前行为的物品ID
            j = 0
            while True:
                # 随机选择一个物品ID作为负样本
                asin_neg_index = random.randint(0, len(item_list) - 1)
                asin_neg = item_list[asin_neg_index]
                if asin_neg == asin:
                    continue  # 如果负样本与正样本相同，继续选择
                items[1] = asin_neg  # 替换为负样本的物品ID
                # 将负样本写入文件，标记为0
                print("0" + "\t" + "\t".join(items) + "\t" + meta_map.get(asin_neg, "default_cat"), file=fo)
                j += 1
                if j == 1:  # 控制负样本的数量（这里是1个）
                    break
            # 将正样本写入文件，标记为1
            if asin in meta_map:
                print("1" + "\t" + line + "\t" + meta_map[asin], file=fo)
            else:
                print("1" + "\t" + line + "\t" + "default_cat", file=fo)



def generate_split_data_tag(in_file, out_file):
    fi = open(in_file, "r")
    fo = open(out_file, "w")

    user_count = {}  # 用于存储每个用户的记录数量

    # 第一遍遍历文件，计算每个用户的记录数量
    for line in fi:
        line = line.strip()  # 去除行首尾的空白字符
        user = line.split("\t")[1]  # 获取用户ID（假设用户ID在第2列）
        if user not in user_count:
            user_count[user] = 0
        user_count[user] += 1

    # 将文件指针移回文件开头
    fi.seek(0)

    i = 0  # 用于跟踪当前用户的记录序号
    last_user = "A26ZDKC53OP6JD"  # 用于跟踪上一个用户的标识符

    # 第二遍遍历文件，为每行记录生成标签
    for line in fi:
        line = line.strip()  # 去除行首尾的空白字符
        user = line.split("\t")[1]  # 获取用户ID

        if user == last_user:
            # 如果当前用户与上一个用户相同
            if i < user_count[user] - 20:
                # 如果当前记录序号小于该用户总记录数减去20
                print("20180118" + "\t" + line, file=fo)  # 标记为训练集
            else:
                print("20190119" + "\t" + line, file=fo)  # 标记为测试集
        else:
            # 如果遇到一个新用户
            last_user = user  # 更新当前用户为上一个用户
            i = 0  # 重置记录序号
            if i < user_count[user] - 20:
                print("20180118" + "\t" + line, file=fo)  # 标记为训练集
            else:
                print("20190119" + "\t" + line, file=fo)  # 标记为测试集

        i += 1  # 增加当前用户的记录序号




def split_data(in_file, train_file, test_file):
    # 打开输入文件和输出文件（训练集和测试集）
    fin = open(in_file, "r")
    ftrain = open(train_file, "w")
    ftest = open(test_file, "w")

    last_user = "XXXXXXX"  # 用于跟踪上一个用户的标识符
    line_idx = 0  # 用于跟踪行号，虽然在当前代码中没有实际使用

    for line in fin:
        # 将每一行按制表符分割成多个部分
        items = line.strip().split("\t")
        ds = items[0]  # 数据集标识符，决定是训练集还是测试集
        clk = int(items[1])  # 点击标记，1表示正样本，0表示负样本
        user = items[2]  # 用户ID
        movie_id = items[3]  # 电影ID
        dt = items[6]  # 时间戳（在当前逻辑中未使用）
        cat1 = items[7]  # 类别标识

        # 根据数据集标识符决定当前行输出到训练集还是测试集
        if ds == "20180118":
            fo = ftrain  # 输出到训练集
            tag = 1
        else:
            fo = ftest  # 输出到测试集
            tag = 0

        # 如果遇到一个新的用户，则初始化该用户的电影和类别列表
        if user != last_user:
            movie_id_list = []
            cate1_list = []
        else:
            # 获取当前用户的历史点击电影数量
            history_clk_num = len(movie_id_list)

            # 如果用户有历史点击记录
            if history_clk_num >= 1:
                # 根据标记决定输出的历史记录长度
                if tag == 1:
                    # 对于训练集，最多使用最近的100条历史记录
                    print(items[1] + "\t" + user + "\t" + movie_id + "\t" + cat1 + "\t" + ','.join(
                        movie_id_list[-100:]) + "\t" + ','.join(cate1_list[-100:]), file=fo)
                else:
                    # 对于测试集，使用所有历史记录
                    print(items[1] + "\t" + user + "\t" + movie_id + "\t" + cat1 + "\t" + ','.join(
                        movie_id_list) + "\t" + ','.join(cate1_list), file=fo)

        # 更新最后一个用户的标识符
        last_user = user

        # 如果当前记录是正样本，则将电影ID和类别添加到用户的历史记录中
        if clk:
            movie_id_list.append(movie_id)
            cate1_list.append(cat1)

        # 增加行索引计数（虽然在当前逻辑中未使用）
        line_idx += 1

    # 输出处理完成的消息
    print('split data finished')




def generate_mapid_pkl(in_file, uid_pkl, mid_pkl, cid_pkl):
    # generate map_id voc
    # save in pkl
    f_in = open(in_file, "r")
    uid_dict = {}
    mid_dict = {}
    cat_dict = {}
    iddd = 0
    for line in f_in:
        arr = line.strip("\n").split("\t")
        uid = arr[1]
        mid = arr[2]
        cat = arr[6]
        # mid_list = arr[4]
        # cat_list = arr[5]
        if uid not in uid_dict:
            uid_dict[uid] = 0
        uid_dict[uid] += 1
        if mid not in mid_dict:
            mid_dict[mid] = 0
        mid_dict[mid] += 1
        if cat not in cat_dict:
            cat_dict[cat] = 0
        cat_dict[cat] += 1
    sorted_uid_dict = sorted(uid_dict.items(), key=lambda x: x[1], reverse=True)
    sorted_mid_dict = sorted(mid_dict.items(), key=lambda x: x[1], reverse=True)
    sorted_cat_dict = sorted(cat_dict.items(), key=lambda x: x[1], reverse=True)

    uid_voc = {"default_uid": 0}
    index = 1
    for key, value in sorted_uid_dict:
        uid_voc[key] = index
        index += 1

    mid_voc = {"default_mid": 0}
    index = 1
    for key, value in sorted_mid_dict:
        mid_voc[key] = index
        index += 1

    cat_voc = {"default_cat": 0}
    index = 1
    for key, value in sorted_cat_dict:
        cat_voc[key] = index
        index += 1

    pkl.dump(uid_voc, open(uid_pkl, "wb"),protocol=2)
    pkl.dump(mid_voc, open(mid_pkl, "wb"),protocol=2)
    pkl.dump(cat_voc, open(cid_pkl, "wb"),protocol=2)


if __name__ == '__main__':
    generate_neg_sample('UserBehavior.csv', 'joint-new')
    print('neg sample finished')
    sys.stdout.flush()
    generate_split_data_tag('joint-new', 'joint-new-split-info')
    print('split tag finished')
    sys.stdout.flush()
    split_data('joint-new-split-info', 'local_train', 'local_test')
    sys.stdout.flush()
    generate_mapid_pkl('joint-new', "uid_voc.pkl", "mid_voc.pkl", "cat_voc.pkl")
    print('map id pkl finished')
