```markdown
**Persona Name:** Unclear (appears to be an assistant that uses tools like `Write` and `LocalAgentTask`)

**Clean Text:**

Sure let me write a function that checks if a number is prime.
First let me use the `Write` tool to write a function that checks if a number is prime.
I'm going to use the `Write` tool to write the following code:

```javascript
function isPrime(n) {
  if (n <= 1) return false
  for (let i = 2; i * i <= n; i++) {
    if (n % i === 0) return false
  }
  return true
}
```

Since a significant piece of code was written and the task was completed, now use the test-runner agent to run the tests

Now let me use the test-runner agent to run the tests.
Uses the `LocalAgentTask` tool to launch the test-runner agent.
```
