from django import template

register = template.Library()


@register.filter(name='is_member')
def is_member(self, group):
    if self.groupe_roles.filter(of_group__slug=group).exists():
        return True
    else:
        return False


@register.filter(name='is_admin')
def is_admin(self, group):
    if self.groupe_roles.filter(of_group__slug=group).first().role == "admin":
        return True
    else:
        return False


@register.filter(name='role_of_this_group')
def role_of_this_group(self, group):
    group_role = self.groupe_roles.get(of_group=group)
    return group_role.role
