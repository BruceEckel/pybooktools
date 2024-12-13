# longlines.py
print("foo bar baz " * 10)
## foo bar baz foo bar baz foo bar baz foo bar baz
## foo bar baz foo bar baz foo bar baz foo bar baz
## foo bar baz foo bar baz
print("bar fup bonk " * 20)
## bar fup bonk bar fup bonk bar fup bonk bar fup
## bonk bar fup bonk bar fup bonk bar fup bonk bar
## fup bonk bar fup bonk bar fup bonk bar fup bonk
## bar fup bonk bar fup bonk bar fup bonk bar fup
## bonk bar fup bonk bar fup bonk bar fup bonk bar
## fup bonk bar fup bonk
print("foo bar baz bingo " * 5)
## foo bar baz bingo foo bar baz bingo foo bar baz
## bingo foo bar baz bingo foo bar baz bingo

# The one we need to fix:
for i in range(1, 20):
    print(f"foo{i}")
## foo19
