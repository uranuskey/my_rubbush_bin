import os
import shutil


def collect_folders(main_folder):
    """
    遍历指定主文件夹下的子文件夹，收集特定的子子文件夹到collect文件夹中。

    Args:
        main_folder (str): 主文件夹的路径。
    """

    collect_path = os.path.join(main_folder, "collect")

    # 创建collect文件夹，如果它不存在的话
    os.makedirs(collect_path, exist_ok=True)
    print(f"确保 'collect' 文件夹存在于: {collect_path}")

    # 遍历main_folder下的所有一级子文件夹 (例如 1, 2, 3)
    for sub_folder_name in os.listdir(main_folder):
        sub_folder_path = os.path.join(main_folder, sub_folder_name)

        # 确保它是一个文件夹且不是collect文件夹本身
        if os.path.isdir(sub_folder_path) and sub_folder_name != "collect":
            print(f"\n正在处理文件夹: {sub_folder_name}")

            # 遍历一级子文件夹下的所有子子文件夹 (例如 a, b, c)
            for inner_folder_name in os.listdir(sub_folder_path):
                inner_folder_path = os.path.join(sub_folder_path, inner_folder_name)

                # 确保它是一个文件夹
                if os.path.isdir(inner_folder_path):
                    # 检查是否是需要收集的文件夹 (a, b, c)
                    # 脚本会收集所有二级子文件夹，如果你只想收集a,b,c，可以取消下面这行的注释并修改
                    # if inner_folder_name not in ['a', 'b', 'c']:
                    #    continue

                    target_inner_folder_path = os.path.join(collect_path, inner_folder_name)

                    # 如果collect文件夹中还没有这个子子文件夹，则创建它
                    if not os.path.exists(target_inner_folder_path):
                        os.makedirs(target_inner_folder_path)
                        print(f"创建了 '{inner_folder_name}' 在 '{collect_path}'")

                    # 复制源文件夹中的所有文件到目标文件夹
                    print(
                        f"正在复制 '{inner_folder_name}' 的内容从 '{sub_folder_name}' 到 'collect/{inner_folder_name}'")
                    for item_name in os.listdir(inner_folder_path):
                        src_item_path = os.path.join(inner_folder_path, item_name)
                        dst_item_path = os.path.join(target_inner_folder_path, item_name)

                        if os.path.isfile(src_item_path):
                            # 如果目标文件已存在，则会覆盖。如果需要更复杂的合并逻辑（如询问、重命名），需要修改此处。
                            shutil.copy2(src_item_path, dst_item_path)  # copy2 会复制元数据
                            print(f"  - 复制文件: {item_name}")
                        elif os.path.isdir(src_item_path):
                            # 如果子文件夹中还有子文件夹，则递归复制整个文件夹
                            # dirs_exist_ok=True 允许目标文件夹已经存在，并合并内容
                            shutil.copytree(src_item_path, dst_item_path, dirs_exist_ok=True)
                            print(f"  - 复制文件夹: {item_name}")


# 使用示例
if __name__ == "__main__":
    # 请将这里的路径替换为你的实际路径
    main_folder_path = r"C:\Users\w1396\Downloads\魔改10月增量包\魔改10月增量包"

    print(f"即将开始收集操作，主文件夹为: {main_folder_path}")

    # 运行收集函数
    collect_folders(main_folder_path)

    print("\n收集操作完成！")
    print(f"检查 '{os.path.join(main_folder_path, 'collect')}' 文件夹查看结果。")
