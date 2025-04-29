# Markdown Presentation Example

This is a sample Markdown file to test the presentation tool.

## First Section

- This is a bullet point
- Another bullet point

### Subsection

- Nested bullet point
- Another nested bullet point

## Code Example

Here's a Python code example:

```python
def hello_world():
    """Print a greeting message."""
    print("Hello, world!")
    
    # This is a comment
    for i in range(5):
        print(f"Count: {i}")
        
    return "Done"

if __name__ == "__main__":
    result = hello_world()
    print(result)
```

## Another Section

This section demonstrates more features.

### Math Example

```python
import numpy as np
import matplotlib.pyplot as plt

def plot_sine_wave():
    # Generate x values
    x = np.linspace(0, 2 * np.pi, 100)
    
    # Calculate sine values
    y = np.sin(x)
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, 'b-', linewidth=2)
    plt.title('Sine Wave')
    plt.xlabel('x')
    plt.ylabel('sin(x)')
    plt.grid(True)
    plt.show()
    
plot_sine_wave()
```

## Final Thoughts

- The presentation tool makes it easy to create slides from Markdown
- Code examples are syntax highlighted
- Navigation is simple with keyboard shortcuts