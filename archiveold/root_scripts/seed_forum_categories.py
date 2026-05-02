import sys
sys.path.insert(0, '.')
from app.services import sk_kernel_instance
print('Available plugins:')
for plugin_name in sk_kernel_instance.kernel.plugins:
    print(f'  - {plugin_name}:')                                                                                                                       
    for func_name in sk_kernel_instance.kernel.plugins[plugin_name]:
         print(f'    - {func_name}')