// HelloWorld.cdc
//
// Welcome to Cadence! This is one of the simplest programs you can deploy on Flow.
//
// The HelloWorld contract contains a single string field and a public getter function.
//
// Follow the "Hello, World!" tutorial to learn more: https://docs.onflow.org/cadence/tutorial/02-hello-world/
pub contract HelloWorld {
  // Declare a public field of type String.
  //
  // All fields must be initialized in the init() function.
  pub var greeting: String

  // Public function that returns our friendly greeting!
  access(all) fun changeGreeting(newGreeting: String) {
    self.greeting = newGreeting
  }

  // Public function that returns our friendly greeting!
  access(all) fun hello(): String {
      return self.greeting
  }

  // The init() function is required if the contract contains any fields.
  init() {
    self.greeting = "Hello, World!"
  }
}