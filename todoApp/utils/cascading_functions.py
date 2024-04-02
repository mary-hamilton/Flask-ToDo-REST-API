# def search_todo_tree(todo, target_todo):
#     if todo == target_todo:
#         return True
#     if todo.children:
#         for child in todo.children:
#             if search_todo_tree(child, target_todo):
#                 return True
#     return False

def apply_todo_tree(todo, function, return_result=False):
    function(todo)
    if return_result and function(todo):
        return True
    if todo.children:
        for child in todo.children:
            if apply_todo_tree(child, function, return_result):
                return True
    if return_result:
        return False


def make_todo_checked(todo):
    todo.checked = True


def make_todo_matcher(target_todo):
    def match_todo(todo):
        if target_todo == todo:
            return True
    return match_todo

