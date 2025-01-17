# Copyright (c) 2018 Alexander Todorov <atodorov@MrSenko.com>

# Licensed under the GPL 2.0: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# NOTE: import order matches the numeric ID of the checker
from .dunder_attributes import DunderClassAttributeChecker
from .list_comprehension import ListComprehensionChecker
from .docstring import DocstringChecker
from .raw_sql import RawSQLChecker
from .auth_user import AuthUserChecker
from .bulk_create import BulkCreateChecker
from .objects_update import ObjectsUpdateChecker
from .tags import TagsChecker
from .empty import EmptyModuleChecker
from .empty import ModuleInDirectoryWithoutInitChecker
from .empty import EmptyClassChecker
from .nested_definition import NestedDefinitionChecker
from .missing_permissions import MissingPermissionsChecker
from .auto_field import AutoFieldChecker
from .one_to_one_field import OneToOneFieldChecker


def register(linter):
    linter.register_checker(DunderClassAttributeChecker(linter))
    linter.register_checker(ListComprehensionChecker(linter))
    linter.register_checker(DocstringChecker(linter))
    linter.register_checker(RawSQLChecker(linter))
    linter.register_checker(AuthUserChecker(linter))
    linter.register_checker(BulkCreateChecker(linter))
    linter.register_checker(ObjectsUpdateChecker(linter))
    linter.register_checker(TagsChecker(linter))
    linter.register_checker(EmptyModuleChecker(linter))
    linter.register_checker(ModuleInDirectoryWithoutInitChecker(linter))
    linter.register_checker(EmptyClassChecker(linter))
    linter.register_checker(NestedDefinitionChecker(linter))
    linter.register_checker(MissingPermissionsChecker(linter))
    linter.register_checker(AutoFieldChecker(linter))
    linter.register_checker(OneToOneFieldChecker(linter))
