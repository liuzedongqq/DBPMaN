import random
import pickle as pkl
import sys

def generate_neg_sample(in_file, out_file):
    item_list = []
    user_map = {}

    # UserID,ItemID,CategoryID,BehaviorType,Timestamp

    fi = open(in_file, "r")
    for line in fi:
        item = line.strip().split(',')
        if item[0] not in user_map:
            user_map[item[0]] = []
        user_map[item[0]].append(("\t".join(item), float(item[-1])))
        item_list.append(item[1])

    fi = open(in_file, 'r')
    meta_map = {}  # meta_map记录item_category映射
    for line in fi:
        arr = line.strip().split(",")
        if arr[1] not in meta_map:
            meta_map[arr[1]] = arr[2]

    fo = open(out_file, "w")
    for key in user_map:
        sorted_user_bh = sorted(user_map[key], key=lambda x: x[1])
        for line, t in sorted_user_bh:
            items = line.split("\t")
            asin = items[1]  # ItemId
            j = 0
            while True:
                asin_neg_index = random.randint(0, len(item_list) - 1)
                asin_neg = item_list[asin_neg_index]
                if asin_neg == asin:
                    continue
                items[1] = asin_neg
                print("0" + "\t" + "\t".join(items) + "\t" + meta_map[asin_neg], file=fo)
                j += 1
                if j == 1:  # negative sampling frequency
                    break
            if asin in meta_map:
                print("1" + "\t" + line + "\t" + meta_map[asin], file=fo)
            else:
                print("1" + "\t" + line + "\t" + "default_cat", file=fo)


def generate_split_data_tag(in_file, out_file):
    fi = open(in_file, "r")
    fo = open(out_file, "w")
    user_count = {}
    for line in fi:
        line = line.strip()
        user = line.split("\t")[1]
        if user not in user_count:
            user_count[user] = 0
        user_count[user] += 1
    fi.seek(0)
    i = 0
    last_user = "A26ZDKC53OP6JD"
    for line in fi:
        line = line.strip()
        user = line.split("\t")[1]
        if user == last_user:
            if i < user_count[user] - 20:  # 1 + negative samples
                print("20180118" + "\t" + line, file=fo)
            else:
                print("20190119" + "\t" + line, file=fo)
        else:
            last_user = user
            i = 0
            if i < user_count[user] - 20:
                print("20180118" + "\t" + line, file=fo)
            else:
                print("20190119" + "\t" + line, file=fo)
        i += 1

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
