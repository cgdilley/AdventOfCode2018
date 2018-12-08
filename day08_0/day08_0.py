
def main():
    with open("../input/day8.txt", "r") as f:
        numbers = [int(x) for x in f.read().split(" ")]

    nodes = parse_nodes(numbers)

    print(sum_all_meta(nodes))


def parse_nodes(numbers):
    """
    This method is an abomination, forcing that which should be recursive into
    something horrifically iterative.  See commented-out function below
    for recursive version (which didn't work due to stack overflow...)

    The general idea here is that there are two modes: child-processing mode
    and metadata-processing mode.
    While in child-processing mode, we keep continuously reading child- and metadata-
    counts and instantiating new nodes, building up the current branch that
    represents a child hierarchy... children of children of children, etc.

    If at any point we find a node that has finished processing its children
    (ie. the number of children in its children list equals the child count it was
    initially assigned... which may be 0), then we switch into metadata-processing mode.

    This mode will read metadata values into the current node and then pop the node off of the
    current branch.  It will then check if its parent node has also finished processing
    its children;  if it has, this process repeats and it remains in metadata-processing
    mode.  Otherwise, it switches back into child-processing mode again.

    This process continues until the root node has had all its children processed and is
    popped off of the current branch.

    :param numbers: The number sequence to build nodes from
    :return: A list of all nodes in the order they were generated
    """

    # Tracks the nodes that comprise the current branch, where each element
    # is a child of the element before it (and curr_branch[0] is the root)
    curr_branch = []

    # The list to collect all nodes into
    all_nodes = []

    # Start from the beginning
    index = 0

    # Spoopy infinite while, returns directly out of function to break the loop
    # This loop represents the "child-processing mode"
    while True:
        # Start by reading two number values, representing child and metadata counts
        child_count = numbers[index]
        meta_count = numbers[index + 1]

        # Create the node object, instantiating empty children and meta lists
        node = {
            "child_count": child_count,
            "meta_count": meta_count,
            "start_index": index,
            "children": [],
            "meta": []
        }
        # Add the node to the master list
        all_nodes.append(node)

        # Advance the index
        index += 2

        # If that node isn't the root node, add it as a child of its parent
        if len(curr_branch) > 0:
            curr_branch[-1]["children"].append(node)

        # Expand the current branch with the node just generated
        curr_branch.append(node)

        # Another spoopy infinite while that contains the return call for both
        # infinite whiles.
        # This loop represents the "metadata-processing mode".
        while True:

            # If we've popped the root off of the current branch, we're done.  Woohoo!
            if len(curr_branch) == 0:
                return all_nodes

            # Get the node that is currently at the bottom of the current branch
            bottom = curr_branch[-1]

            # If this node isn't done processing its children, break out of this
            # while loop and go back to child-processing mode
            if bottom["child_count"] != len(bottom["children"]):
                break

            # Otherwise if the node is done processing children, read the next number
            # of entries as meta data entries, then advance the index appropriately
            for i in range(bottom["meta_count"]):
                bottom["meta"].append(numbers[index + i])

            index += bottom["meta_count"]

            # Since this node is done, pop it off of the current branch
            del curr_branch[-1]


# I'm sure this can be done more cleverly but whatever
def sum_all_meta(nodes):
    s = 0
    for node in nodes:
        for meta in node["meta"]:
            s += meta
    return s

# So this would have been the nice and convenient recursive method,
# if I hadn't run into stack overflow issues

# def parse_node(numbers, start_index):
#
#     child_count = numbers[start_index]
#     meta_count = numbers[start_index + 1]
#
#     index = start_index + 2
#
#     children = []
#     for _ in range(child_count):
#         child = parse_node(numbers, index)
#         index = child["end_index"] + 1
#         children.append(child)
#
#     meta = numbers[index:index + meta_count]
#
#     return {
#         "child_count": child_count,
#         "meta_count": meta_count,
#         "children": children,
#         "meta": meta,
#         "start_index": start_index,
#         "end_index": index + meta_count
#     }


#

main()



