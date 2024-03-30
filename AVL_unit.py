import sys


# Generic tree node class
class TreeNode(object):
    def __init__(self, order_id, current_system_time,
                 order_value, delivery_time):
        self.order_id = order_id
        self.current_system_time = current_system_time
        self.order_value = order_value
        self.delivery_time = delivery_time
        self.ETA = None
        self.priority = 0.3 * (self.order_value / 50) - \
                        (0.7 * current_system_time)

        self.left = None
        self.right = None
        self.height = 1


# AVL tree class which supports insertion,
# deletion operations
class AVL_Tree(object):
    def __init__(self):
        self.root = None

    def insert(self, root, node):

        # Step 1 - Perform normal BST
        if not root:
            return node
        elif node.priority < root.priority:
            root.left = self.insert(root.left, node)
        else:
            root.right = self.insert(root.right, node)

        # Step 2 - Update the height of the
        # ancestor node
        root.height = 1 + max(self.getHeight(root.left),
                              self.getHeight(root.right))

        # Step 3 - Get the balance factor
        balance = self.getBalance(root)

        # Step 4 - If the node is unbalanced,
        # then try out the 4 cases
        # Case 1 - Left Left
        if balance > 1 and node.priority < root.left.priority:
            return self.rightRotate(root)

        # Case 2 - Right Right
        if balance < -1 and node.priority > root.right.priority:
            return self.leftRotate(root)

        # Case 3 - Left Right
        if balance > 1 and node.priority > root.left.priority:
            root.left = self.leftRotate(root.left)
            return self.rightRotate(root)

        # Case 4 - Right Left
        if balance < -1 and node.priority < root.right.priority:
            root.right = self.rightRotate(root.right)
            return self.leftRotate(root)

        return root

    def leftRotate(self, z):

        y = z.right
        T2 = y.left

        # Perform rotation
        y.left = z
        z.right = T2

        # Update heights
        z.height = 1 + max(self.getHeight(z.left),
                           self.getHeight(z.right))
        y.height = 1 + max(self.getHeight(y.left),
                           self.getHeight(y.right))

        # Return the new root
        return y

    def rightRotate(self, z):

        y = z.left
        T3 = y.right

        # Perform rotation
        y.right = z
        z.left = T3

        # Update heights
        z.height = 1 + max(self.getHeight(z.left),
                           self.getHeight(z.right))
        y.height = 1 + max(self.getHeight(y.left),
                           self.getHeight(y.right))

        # Return the new root
        return y

    def getHeight(self, root):
        if not root:
            return 0

        return root.height

    def getBalance(self, root):
        if not root:
            return 0

        return self.getHeight(root.left) - self.getHeight(root.right)

    def getMinValueNode(self, root):
        if root is None or root.left is None:
            return root

        return self.getMinValueNode(root.left)

    def preOrder(self, root, tmp_list=None):
        if tmp_list is None:
            tmp_list = []
        if not root:
            return

        self.preOrder(root.left, tmp_list)
        # print("{0} ".format(root.order_id), end="")
        # print(root.order_id)
        tmp_list.append(root)
        self.preOrder(root.right, tmp_list)
        return tmp_list

    def inOrder(self, root, tmp_list=None):
        # in priority order, see insert
        if tmp_list is None:
            tmp_list = []
        if not root:
            return
        self.inOrder(root.right, tmp_list)
        tmp_list.append(root)
        self.inOrder(root.left, tmp_list)
        return tmp_list

    def get_path(self, root, orderId):
        # get the path from node to root
        if root is None:
            return []
        if root.order_id == orderId:
            return [root]

        left_path = self.get_path(root.left, orderId)
        if left_path:
            left_path.append(root)
            return left_path

        right_path = self.get_path(root.right, orderId)
        if right_path:
            right_path.append(root)
            return right_path

        return []

    def get_near_large_node(self, root, orderId):
        path = self.get_path(root, orderId)
        if path[0].right:
            right = path[0].right
            while right.left:
                right = right.left
            return right
        for path_node in path:
            if path_node.priority > path[0].priority:
                # print(str(path_node.priority)+ " "+str (path[0].priority))
                return path_node

    def printHelper(self, currPtr, indent, last):
        if currPtr is not None:
            sys.stdout.write(indent)
            if last:
                sys.stdout.write("R----")
                indent += "     "
            else:
                sys.stdout.write("L----")
                indent += "|    "
            print(currPtr.priority)
            self.printHelper(currPtr.left, indent, False)
            self.printHelper(currPtr.right, indent, True)


if __name__ == "__main__":
    # For animation, check out:
    # https://www.cs.usfca.edu/~galles/visualization/AVLtree.html
    pass
    # myTree = AVL_Tree()
    # _root = None
    # nums = [9, 5, 10, 1, 6, 11, 0, 2, 3]
    # # nums = [10, 20, 30, 40, 50]
    #
    # for order_id, num in enumerate(nums):
    #     _root = myTree.insert(_root, order_id+100, num)
    #
    # # Preorder Traversal
    # print(f"Preorder Traversal after insertion - {nums}")
    # pre_order = myTree.preOrder(_root)
    # in_order = myTree.inOrder(_root)
    # array = []
    # # in_order2 = myTree.getAllOrderInOrder(_root, array)
    # # for i in array:
    # #     print("---id:", i.order_id)
    # print("pre order", pre_order)
    # print("in order", in_order)
    # # print("\n", in_order2)
    # print()
    # myTree.printHelper(_root, "", True)
    #
    # # Delete
    # num = 10
    # # num = 30
    # root = myTree.delete(_root, num)
    #
    #
    # # Preorder Traversal
    # print(f"Preorder Traversal after deletion - {num}")
    # myTree.preOrder(root)
    # print()
    # myTree.printHelper(root, "", True)
