# Recieve arguments for decorator function
def custom_fence(fence: str = "+"):
    # Decorator function
    def add_fence(func):
        # Original function wrapper
        def wrapper(text: str):
            print(fence * len(text))
            func(text)
            print(fence * len(text))
        
        return wrapper
    
    return add_fence


# Use custom decorator
@custom_fence("x")
def log(text: str):
    print(text)


# Call function with defined name
log("ballon")
