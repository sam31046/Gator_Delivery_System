from AVL_unit import AVL_Tree


class Order:
    def __init__(self, order_id, current_system_time, order_value, delivery_time):
        self.order_id = order_id
        self.current_system_time = current_system_time
        self.order_value = order_value
        self.delivery_time = delivery_time
        self.priority = self.calculate_priority()
        self.ETA = 0  # 初始设为0，后续根据逻辑计算

    def calculate_priority(self):
        value_weight = 0.3
        time_weight = 0.7
        normalized_order_value = self.order_value / 50
        return value_weight * normalized_order_value - time_weight * self.current_system_time

class OrderManagementSystem:
    def __init__(self):
        self.orders_by_priority = AVL_Tree()  # 按优先级组织的AVL树
        self.orders_by_eta = AVL_Tree()  # 按ETA组织的AVL树
        self.current_time = 0  # 系统当前时间，根据创建订单时更新
        self.last_delivery_time = 0  # 记录上一个订单的送达时间
        self.last_comeback = 0  # Last duration per trip, for comeback
        self.order_count = 0
        self._root_pri = None
        self._root_eta = None

    def create_order(self, order_id, current_system_time, order_value, delivery_time):
        """
        :param order_id:
        :param current_system_time:
        :param order_value:
        :param delivery_time: Time spend on delivery
        :return:
        """

        # 更新系统时间
        self.current_time = current_system_time
        # 创建新订单
        new_order = Order(order_id, self.current_time, order_value, delivery_time)
        # 计算ETA
        if self.order_count == 0:  # The first order
            new_order.ETA = self.current_time + delivery_time
            self.last_comeback = delivery_time
            # print("first")
        else:
            # Last ETA + Last comeback + Current delivery spend
            new_order.ETA = self.last_delivery_time + self.last_comeback + delivery_time
            self.last_comeback = delivery_time

        # 更新最后一个订单的送达时间
        self.last_delivery_time = new_order.ETA
        # 将新订单插入到AVL树中
        self._root_pri = self.orders_by_priority.insert(self._root_pri,
                                                 new_order.priority)
        self._root_eta = self.orders_by_eta.insert(self._root_eta,
                                            new_order.ETA)
        # 打印ETA
        print(f"Order {order_id} has been created - ETA: {new_order.ETA}")

        self.order_count += 1
        # print(self.order_count)
        # TODO: 根据逻辑更新其他订单的ETA

        self.print_trees()

    def update_delivered_orders(self):
        """
        检查已送达的订单并更新状态
        """
        current_time = self.current_time
        delivered_orders = []

        # 遍历订单按ETA排序的AVL树
        for eta in self.orders_by_eta.preOrder(self._root_eta):
            if eta > current_time:
                # 如果订单的ETA大于当前时间，跳出循环
                break
            # 获取订单
            order = self.orders_by_eta.search(self._root_eta, eta).data
            if order.delivered:
                # 如果订单已送达，继续下一个订单
                continue
            # 标记订单为已送达
            order.delivered = True
            # 将订单添加到已送达订单列表中
            delivered_orders.append(order)


    def cancel_order(self, order_id, current_system_time):
        # 在AVL树中查找要取消的订单，并从树中移除
        # 这里假设AVL树的remove方法已经正确实现
        # 你需要根据order_id从两个AVL树中分别移除订单
        self._root_pri = self.orders_by_priority.remove(self._root_pri, order_id)
        self._root_eta = self.orders_by_eta.remove(self._root_eta, order_id)

        # TODO: 更新所有具有较低优先级的订单的ETA
        # 这可能需要遍历AVL树并更新每个节点的ETA

        print(f"Order {order_id} has been canceled")

    def get_rank_of_order(self, order_id):
        # 在AVL树中查找order_id对应的订单，并获取其在树中的排名
        # 这里假设AVL树的rank方法已经正确实现
        # 你需要根据order_id从优先级AVL树中找到订单并获取其排名
        rank = self.orders_by_priority.rank(self._root_pri, order_id)
        print(f"Order {order_id} will be delivered after {rank} orders")

    def update_time(self, order_id, current_system_time, new_delivery_time):
        # 在AVL树中查找要更新时间的订单，并根据新的delivery_time更新ETA
        # 这里假设AVL树的search方法已经正确实现
        # 你需要根据order_id从两个AVL树中分别找到订单并更新ETA
        # 更新ETA后，你可能需要重新平衡AVL树
        self.orders_by_priority.remove(self._root_pri, order_id)
        self.orders_by_eta.remove(self._root_eta, order_id)

        # 更新delivery_time
        order = self.orders_by_priority.search(self._root_pri, order_id)
        order.delivery_time = new_delivery_time
        order.ETA = current_system_time + new_delivery_time

        # 重新插入订单并更新树的根节点
        self._root_pri = self.orders_by_priority.insert(self._root_pri, order.priority)
        self._root_eta = self.orders_by_eta.insert(self._root_eta, order.ETA)

        print(f"Updated ETAs: [{order_id}: {order.ETA}]")

    def print_trees(self):
        print("\n==============================")
        print(">>> Priority Tree:")
        self.orders_by_priority.preOrder(self._root_pri)
        print()
        self.orders_by_priority.printHelper(self._root_pri, "", True)

        print(">>> ETA Tree:")
        self.orders_by_eta.preOrder(self._root_eta)
        print()
        self.orders_by_eta.printHelper(self._root_eta, "", True)
        print("==============================\n")

    def print_orders_within_time(self, time1, time2):
        # 打印在给定时间范围内的订单
        orders_within_time = []

        # 在ETA AVL树中查找所有ETA位于给定时间范围内的订单
        self.find_orders_within_time(self._root_eta, time1, time2, orders_within_time)

        if orders_within_time:
            print("Orders to be delivered within the given time range:")
            print(orders_within_time)
        else:
            print("There are no orders in that time period")

    def find_orders_within_time(self, root, time1, time2, orders_within_time):
        # 递归遍历ETA AVL树，查找在给定时间范围内的订单
        if root is None:
            return

        if time1 <= root.val <= time2:
            order = self.orders_by_eta.search(root, root.val)
            if order is not None and order.val > self.current_time:
                orders_within_time.append(order.order_id)

        if root.val >= time1:
            self.find_orders_within_time(root.left, time1, time2, orders_within_time)

        if root.val <= time2:
            self.find_orders_within_time(root.right, time1, time2, orders_within_time)


# Example usage:
oms = OrderManagementSystem()

# Creating orders
oms.create_order(1001, 1, 100, 4)
oms.create_order(1002, 2, 150, 7)
oms.create_order(1003, 8, 50, 2)
oms.print_orders_within_time(2, 15)
oms.create_order(1004, 9, 300, 12)

oms.print_orders_within_time(45, 55)



# Cancelling an order
# oms.cancel_order(1, 3)

# Updating delivery time of an order
# oms.updateTime(2, 4, 3)

# Printing order details
# oms.printOrder(2)

# Printing orders within a time range
# oms.printOrdersWithinTime(2, 5)

# Getting rank of an order
# oms.getRankOfOrder(2)
