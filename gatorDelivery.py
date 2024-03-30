#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from AVL_unit import AVL_Tree, TreeNode
import argparse
import re
import sys


class Order(TreeNode):
    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)


class OrderManagementSystem(AVL_Tree):
    def __init__(self):
        super(OrderManagementSystem, self).__init__()
        self.priority_tree = AVL_Tree()  # 按优先级组织的AVL树
        self.current_time = 0  # 系统当前时间，根据创建订单时更新
        self.last_delivery_time = 0  # 记录上一个订单的送达时间
        self.last_comeback = 0  # Last duration per trip, for comeback
        self.order_count = 0
        self.delivery_time = 0
        self.return_time = 0

    def create_order(self, order_id, current_system_time,
                     order_value, delivery_time):
        # 更新系统时间和交付时间
        self.current_time = current_system_time
        self.delivery_time = delivery_time
        order_delivered = self.get_delivered()

        # 创建新订单
        new_order = Order(order_id, current_system_time,
                          order_value, delivery_time)
        # 将新订单插入到AVL树中
        self.root = self.insert(self.root, new_order)
        # 计算ETA
        larger_node = self.get_near_large_node(self.root, order_id)
        if not larger_node:  # first order
            if self.return_time < current_system_time:
                new_order.ETA = current_system_time + delivery_time
                # self.return_time = current_system_time  # 更新返回时间为当前系统时间
            else:
                new_order.ETA = self.return_time + delivery_time
        else:
            new_order.ETA = larger_node.ETA + larger_node.delivery_time\
                            + new_order.delivery_time

        # 更新最后一个订单的送达时间和返回时间
        # self.last_delivery_time = new_order.ETA
        # self.return_time = current_system_time \
        #     if self.return_time < current_system_time else self.return_time

        # 打印ETA
        print(f"Order {new_order.order_id} has been created - ETA: {new_order.ETA}")
        self.order_count += 1
        self.check_for_order_updates(new_order.order_id)
        self.print_delivered(order_delivered)

    # 检查是否有订单更新
    def check_for_order_updates(self, order_id):
        order_list = self.inOrder(self.root)  # in descend priority order
        if order_list is None:
            return

        index = 0
        # find the index of order_id
        for index, order in enumerate(order_list):
            if order.order_id == order_id:
                break

        # 更新订单的预计送达时间
        # update lower priority orders' ETA
        updated_later_orders = []
        for next_index in range(index + 1, len(order_list)):
            order_list[next_index].ETA = order_list[next_index - 1].ETA + \
                                         order_list[next_index - 1].delivery_time + \
                                         order_list[next_index].delivery_time
            updated_later_orders.append(order_list[next_index])

        # 打印更新后的预计送达时间
        if len(updated_later_orders) != 0:
            s = "Updated ETAs: ["
            for j, order in enumerate(updated_later_orders):
                s += str(order.order_id) + ":" + str(order.ETA)
                if j != len(updated_later_orders) - 1:  # not last one
                    s += ","
            s += "]"
            print(s)

    def cancel_order(self, order_id, current_system_time):
        self.current_time = current_system_time
        order_delivered = self.get_delivered()
        order_list = self.inOrder(self.root)
        found = False
        key = 0
        for key, order in enumerate(order_list):
            if order.order_id == order_id:
                found = True
                break

        if not found:  # order not found
            print(f"Cannot cancel. Order {order_id}"
                  f" has already been delivered.")
        else:
            # assume found
            order_departure_moment = order_list[key].ETA -\
                                     order_list[key].delivery_time
            if order_departure_moment < current_system_time:
                print(f"Cannot cancel. Order {order_id} is out for delivery.")
            else:
                updated_order = []
                if key+1 == len(order_list):
                  pass
                # if the cancelled order was the last order
                # no other order need to be updated
                elif key == 0:
                    # if the cancelled order was originally the next order
                    # and there are at least one order after canceling

                    sec_o = key + 1
                    # decided by the returning time of the delivery agent
                    # Become new first order
                    order_list[sec_o].ETA = self.return_time + \
                                            order_list[sec_o].delivery_time
                    updated_order.append(order_list[sec_o])
                    # Update ETA of subsequent orders after second one
                    for i in range(sec_o + 1, len(order_list)):
                        order_list[i].ETA = order_list[i - 1].ETA + \
                                            order_list[i - 1].delivery_time + \
                                            order_list[i].delivery_time
                        updated_order.append(order_list[i])

                else:
                    # if the cancelled order was not the first order (has order before and after it)
                    # Connect "the order before canceled one" with "the order after canceled one"
                    order_list[key+1].ETA = order_list[key-1].ETA + \
                                            order_list[key-1].delivery_time + \
                                            order_list[key+1].delivery_time
                    updated_order.append(order_list[key+1])
                    # Update ETA of subsequent orders after those two order
                    connect_two = key+1
                    for i in range(connect_two + 1, len(order_list)):
                        order_list[i].ETA = order_list[i - 1].ETA + \
                                            order_list[i - 1].delivery_time + \
                                            order_list[i].delivery_time
                        updated_order.append(order_list[i])

                print(f"Order {order_id} has been canceled")
                if len(updated_order) != 0:
                    s = "Updated ETAs: ["
                    for j, order in enumerate(updated_order):
                        s += str(order.order_id) + ":" + str(order.ETA)
                        if j != len(updated_order) - 1:  # not last one
                            s += ","
                    s += "]"
                    print(s)
                self.root = self.delete(self.root,
                                        order_list[key].priority)
        self.print_delivered(order_delivered)

    def get_rank_of_order(self, order_id):
        # Count how many orders before order_id
        order_list = self.inOrder(self.root)
        count = 0
        for count, order in enumerate(order_list):
            if order.order_id == order_id:
                print(f"Order {order_id} will be delivered"
                      f" after {count} orders.")
                break
        return count

    def update_time(self, order_id, current_system_time, new_delivery_time):
        self.current_time = current_system_time
        order_delivered = self.get_delivered()
        order_list = self.inOrder(self.root)
        found = False
        key = 0
        for key, order in enumerate(order_list):
            if order.order_id == order_id:
                found = True
                break

        if not found:  # order not found
            print(f"Cannot update. Order {order_id}"
                  f" has already been delivered.")
        else:
            order_departure_moment = order_list[key].ETA - \
                                     order_list[key].delivery_time
            if order_departure_moment <= current_system_time:
                print(f"Cannot update. Order {order_id} is out for delivery.")
            else:
                dif = new_delivery_time - order_list[key].delivery_time
                order_list[key].delivery_time = new_delivery_time
                order_list[key].ETA += dif

                for i in range(key+1, len(order_list)):
                    order_list[i].ETA += 2 * dif

                s = "Updated ETAs: ["
                while key < len(order_list):
                    s += str(order_list[key].order_id) + ":" \
                         + str(order_list[key].ETA)
                    if key != len(order_list) - 1:
                        s += ","
                    key += 1
                s += "]"
                print(s)

        self.print_delivered(order_delivered)

    def print_trees(self):
        print("\n==============================")
        print(">>> Priority Tree:")
        # print(self.priority_tree)

        self.preOrder(self.root)
        self.inOrder(self.root)
        print()
        self.printHelper(self.root, "", True)

        print("==============================\n")

    def print_within_time(self, **kwargs):
        time1 = None
        time2 = None

        for key in kwargs:
            if key == "order_id":
                node_list = self.get_path(self.root, kwargs[key])
                print(f"[{node_list[0].order_id},"
                      f" {node_list[0].current_system_time},"
                      f" {node_list[0].order_value},"
                      f" {node_list[0].delivery_time},"
                      f" {node_list[0].ETA} ]")
                return
            if key == "time1":
                time1 = kwargs[key]
            if key == "time2":
                time2 = kwargs[key]

        # Print all orders that will be delivered within the period
        order_list = self.inOrder(self.root)
        result = []
        if order_list is not None:
            for order in order_list:
                if time1 <= order.ETA <= time2:
                    result.append(order)
        if len(result) == 0:
            print("There are no orders in that time period")
        else:
            out = "["
            for key, order in enumerate(result):
                out += str(order.order_id)
                if key != len(result) - 1:  # not last one
                    out += ","
            out += "]"
            print(out)

    def get_delivered(self):
        # get the order that has been delivered
        order_list = self.inOrder(self.root)
        if order_list is None:
            # nothing in tree
            return
        delivered_list = []
        for order in order_list:
            if order.ETA <= self.current_time:
                delivered_list.append(order)
                # self.last_delivery_time = order.ETA
                # self.last_comeback = self.delivery_time
                self.return_time = order.ETA + order.delivery_time
                self.root = self.delete(self.root, order.priority)
            else:
                break
        return delivered_list

    def print_delivered(self, delivered_list=None):
        # print the delivered order
        if delivered_list is None:
            return
            # do nothing
        else:
            for order in delivered_list:
                print(f"Order {order.order_id} has been delivered at time "
                      f"{order.ETA}")

    def quit(self, tmp_list=None):
        if tmp_list is None:
            tmp_list = []
        self.inOrder(self.root, tmp_list)
        for order in range(len(tmp_list)):
            print(f"Order {tmp_list[order].order_id} "
                  f"has been delivered at time {tmp_list[order].ETA}")

    def delete(self, root, priority):

        # Step 1 - Perform standard BST delete
        if not root:
            return root

        elif priority < root.priority:
            root.left = self.delete(root.left, priority)

        elif priority > root.priority:
            root.right = self.delete(root.right, priority)

        else:
            if root.left is None:
                return root.right

            if root.right is None:
                return root.left

            tmp_root = self.getMinValueNode(root.right)
            root.priority = tmp_root.priority
            root.order_id = tmp_root.order_id
            root.current_system_time = tmp_root.current_system_time
            root.order_value = tmp_root.order_value
            root.delivery_time = tmp_root.delivery_time
            root.ETA = tmp_root.ETA
            root.right = self.delete(root.right,
                                     tmp_root.priority)

        # If the tree has only one node,
        # simply return it
        if root is None:
            return root

        # Step 2 - Update the height of the
        # ancestor node
        root.height = 1 + max(self.getHeight(root.left),
                              self.getHeight(root.right))

        # Step 3 - Get the balance factor
        balance = self.getBalance(root)

        # Step 4 - If the node is unbalanced,
        # then try out the 4 cases
        # Case 1 - Left Left
        if balance > 1 and self.getBalance(root.left) >= 0:
            return self.rightRotate(root)

        # Case 2 - Right Right
        if balance < -1 and self.getBalance(root.right) <= 0:
            return self.leftRotate(root)

        # Case 3 - Left Right
        if balance > 1 and self.getBalance(root.left) < 0:
            root.left = self.leftRotate(root.left)
            return self.rightRotate(root)

        # Case 4 - Right Left
        if balance < -1 and self.getBalance(root.right) > 0:
            root.right = self.rightRotate(root.right)
            return self.leftRotate(root)

        return root


def _case():
    # Example usage:
    oms = OrderManagementSystem()

    # Testcase 1
    # oms.create_order(1001, 1, 100, 4)
    # oms.create_order(1002, 2, 150, 7)
    # oms.create_order(1003, 8, 50, 2)
    # oms.print_within_time(2, 15)
    # oms.create_order(1004, 9, 300, 12)
    # oms.get_rank_of_order(1004)
    # oms.print_within_time(45, 55)
    # oms.create_order(1005, 15, 400, 8)
    # oms.create_order(1006, 17, 100, 3)
    # oms.cancel_order(1005, 18)
    # oms.get_rank_of_order(1004)
    # oms.create_order(1007, 19, 600, 7)
    # oms.create_order(1008, 25, 200, 8)
    # oms.update_time(1007, 27, 12)
    # oms.get_rank_of_order(1006)
    # oms.print_within_time(55, 85)
    # oms.create_order(1009, 36, 500, 15)
    # oms.create_order(1010, 40, 250, 10)
    # oms.quit()

    # Example 1
    # oms.create_order(1001, 1, 200, 3)
    # oms.create_order(1002, 3, 250, 6)
    # oms.create_order(1003, 8, 100, 3)
    # oms.create_order(1004, 13, 100, 5)
    # oms.print_within_time(time1=2, time2=15)
    # oms.update_time(1003, 15, 1)
    # oms.create_order(1005, 30, 300, 3)
    # oms.quit

    # Testcase 3
    oms.create_order(4001, 1, 200, 3)
    oms.create_order(4002, 3, 250, 6)
    oms.create_order(4003, 8, 100, 3)
    oms.create_order(4004, 13, 100, 5)
    oms.print_within_time(time1=2, time2=15)
    oms.get_rank_of_order(4003)
    oms.update_time(4003, 15, 2)
    oms.create_order(4005, 17, 150, 4)
    oms.cancel_order(4002, 20)
    oms.create_order(4006, 22, 300, 3)
    oms.print_within_time(time1=10, time2=25)
    oms.create_order(4007, 25, 200, 2)
    oms.create_order(4008, 28, 350, 5)
    oms.print_within_time(time1=20, time2=30)
    oms.get_rank_of_order(4006)
    oms.create_order(4009, 32, 250, 3)
    oms.cancel_order(4004, 34)
    oms.update_time(4005, 37, 5)
    oms.create_order(4010, 40, 400, 6)
    oms.print_within_time(time1=35, time2=45)
    oms.get_rank_of_order(4007)
    oms.create_order(4011, 40, 200, 4)
    oms.create_order(4012, 42, 300, 3)
    oms.print_within_time(time1=50, time2=55)
    oms.update_time(4010, 55, 7)
    oms.cancel_order(4009, 56)
    oms.print_within_time(time1=60, time2=90)
    oms.quit()

    # Testcase 2
    # oms.create_order(3001, 1, 200, 7)
    # oms.create_order(3002, 3, 250, 6)
    # oms.create_order(3003, 8, 1000, 3)
    # oms.create_order(3004, 13, 100, 5)
    # oms.create_order(3005, 15, 300, 4)
    # oms.create_order(3006, 17, 800, 2)
    # oms.print_within_time(time1=2, time2=20)
    # oms.update_time(3004, 20, 2)
    # oms.print_within_time(time1=5, time2=25)
    # oms.cancel_order(3005, 25)
    # oms.print_within_time(time1=10, time2=30)
    # oms.create_order(3007, 30, 200, 3)
    # oms.get_rank_of_order(3005)
    # oms.create_order(3008, 33, 250, 6)
    # oms.create_order(3009, 38, 100, 3)
    # oms.create_order(3010, 40, 4000, 5)
    # oms.get_rank_of_order(3008)
    # oms.create_order(3011, 45, 300, 4)
    # oms.create_order(3012, 47, 150, 2)
    # oms.print_within_time(time1=35, time2=50)
    # oms.get_rank_of_order(3006)
    # oms.quit()


def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()
    return content


def _extract_numbers(text: str):
    numbers = re.findall(r'\d+', text)
    return list(map(int, numbers))


def content_switch(content: list):
    oms = OrderManagementSystem()
    for line in content:
        line = line.lower()
        args = _extract_numbers(line)

        if "createorder" in line:
            oms.create_order(args[0], args[1], args[2], args[3])

        elif "print" in line and len(args) == 2:
            oms.print_within_time(time1=args[0], time2=args[1])

        elif "print" in line and len(args) == 1:
            oms.print_within_time(order_id=args[0])

        elif "getrankoforder" in line:
            oms.get_rank_of_order(args[0])

        elif "cancelorder" in line:
            oms.cancel_order(args[0], args[1])

        elif "updatetime" in line:
            oms.update_time(args[0], args[1], args[2])

        elif "quit" in line:
            oms.quit()
        else:
            print(f"Function not found: {line}")
            exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Read contents of a text file.')
    parser.add_argument('file', metavar='FILE',
                        type=str, help='Path to the text file')

    args = parser.parse_args()
    file_content = read_file(args.file)
    output_file = f"{args.file[:-4]}_output_file.txt"
    with open(output_file, 'w') as sys.stdout:
        content_switch(file_content)


if __name__ == "__main__":
    main()
    # _case()
