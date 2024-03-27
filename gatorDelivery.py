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
            print("first")
        else:
            # Last ETA + Last comeback + Current delivery spend
            new_order.ETA = self.last_delivery_time + self.last_comeback + delivery_time
            self.last_comeback = delivery_time
        # 更新最后一个订单的送达时间
        self.last_delivery_time = new_order.ETA
        # 将新订单插入到AVL树中
        self.orders_by_priority.insert(self.orders_by_priority.root, new_order.priority)
        self.orders_by_eta.insert(self.orders_by_eta.root, new_order.ETA)
        # 打印ETA
        print(f"Order {order_id} has been created - ETA: {new_order.ETA}")

        self.order_count += 1
        print(self.order_count)
        # TODO: 根据逻辑更新其他订单的ETA

    def cancel_order(self, order_id, current_system_time):
        # TODO: 实现取消订单逻辑，包括从AVL树中移除订单，以及可能的ETA更新
        pass

    def get_rank_of_order(self, order_id):
        pass

    def update_time(self, order_id, current_system_time, new_delivery_time):
        pass

# 以下部分是示例性的伪代码，用于展示如何实现一些具体逻辑



# Example usage:
oms = OrderManagementSystem()

# Creating orders
oms.create_order(1001, 1, 100, 4)
oms.create_order(1002, 2, 150, 7)
oms.create_order(1003, 8, 50, 2)

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
