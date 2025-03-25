import * as fs from "fs";
import * as readline from "readline";

// Create a readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

// Function to ask a question and return a promise
const askQuestion = (query: string): Promise<string> => {
  return new Promise((resolve) => rl.question(query, resolve));
};

// Main function to generate a snippet
const generateSnippet = async () => {
  console.log("🔹 VS Code Snippet Generator 🔹");

  const snippetName = await askQuestion("Enter snippet name: ");
  const prefix = await askQuestion("Enter snippet prefix: ");
  const description = await askQuestion("Enter snippet description: ");
  const code = await askQuestion("Enter the code snippet (use \\n for new lines): ");

  const snippetJson = {
    [snippetName]: {
      prefix,
      body: code.split("\\n"), // Convert `\n` into an array for JSON format
      description,
    },
  };

  const fileName = "generated-snippet.code-snippets";
  fs.writeFileSync(fileName, JSON.stringify(snippetJson, null, 2));

  console.log(`✅ Snippet saved in ${fileName}`);
  rl.close();
};

// Run the script
generateSnippet();
