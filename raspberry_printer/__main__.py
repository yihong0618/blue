from .printer import call_printer
from .ci_chang import make_kai_xin_learning_text

if __name__ == "__main__":
    text = make_kai_xin_learning_text({})
    call_printer(None, text)
