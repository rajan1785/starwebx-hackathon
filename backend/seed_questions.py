"""
Seed script to populate the database with sample MCQ and programming questions
"""
from sqlalchemy.orm import Session
from database import SessionLocal
from models import MCQQuestion, ProgrammingProblem

def seed_mcq_questions(db: Session):
    """Add sample MCQ questions"""
    mcq_questions = [
        {
            "question_text": "What is the time complexity of binary search in a sorted array?",
            "option_a": "O(n)",
            "option_b": "O(log n)",
            "option_c": "O(n log n)",
            "option_d": "O(1)",
            "correct_option": "B",
            "difficulty_level": "easy",
            "topic": "algorithms",
            "marks": 1
        },
        {
            "question_text": "Which data structure uses LIFO (Last In First Out) principle?",
            "option_a": "Queue",
            "option_b": "Stack",
            "option_c": "Array",
            "option_d": "Linked List",
            "correct_option": "B",
            "difficulty_level": "easy",
            "topic": "data structures",
            "marks": 1
        },
        {
            "question_text": "In Python, which of the following is mutable?",
            "option_a": "Tuple",
            "option_b": "String",
            "option_c": "List",
            "option_d": "Integer",
            "correct_option": "C",
            "difficulty_level": "easy",
            "topic": "python",
            "marks": 1
        },
        {
            "question_text": "What does SQL stand for?",
            "option_a": "Structured Query Language",
            "option_b": "Simple Question Language",
            "option_c": "Standard Query Language",
            "option_d": "System Query Language",
            "correct_option": "A",
            "difficulty_level": "easy",
            "topic": "databases",
            "marks": 1
        },
        {
            "question_text": "Which HTTP method is used to update a resource?",
            "option_a": "GET",
            "option_b": "POST",
            "option_c": "PUT",
            "option_d": "DELETE",
            "correct_option": "C",
            "difficulty_level": "medium",
            "topic": "web",
            "marks": 1
        },
        {
            "question_text": "What is the space complexity of merge sort?",
            "option_a": "O(1)",
            "option_b": "O(log n)",
            "option_c": "O(n)",
            "option_d": "O(n log n)",
            "correct_option": "C",
            "difficulty_level": "medium",
            "topic": "algorithms",
            "marks": 1
        },
        {
            "question_text": "In OOP, what does polymorphism mean?",
            "option_a": "Hiding data from users",
            "option_b": "Creating multiple objects",
            "option_c": "One interface, multiple implementations",
            "option_d": "Inheriting properties",
            "correct_option": "C",
            "difficulty_level": "medium",
            "topic": "oop",
            "marks": 1
        },
        {
            "question_text": "Which sorting algorithm has best case time complexity of O(n)?",
            "option_a": "Bubble Sort",
            "option_b": "Quick Sort",
            "option_c": "Merge Sort",
            "option_d": "Insertion Sort",
            "correct_option": "D",
            "difficulty_level": "medium",
            "topic": "algorithms",
            "marks": 1
        },
        {
            "question_text": "What is the default port for HTTPS?",
            "option_a": "80",
            "option_b": "443",
            "option_c": "8080",
            "option_d": "3000",
            "correct_option": "B",
            "difficulty_level": "easy",
            "topic": "networking",
            "marks": 1
        },
        {
            "question_text": "In Git, which command is used to create a new branch?",
            "option_a": "git new branch",
            "option_b": "git branch <name>",
            "option_c": "git create branch",
            "option_d": "git add branch",
            "correct_option": "B",
            "difficulty_level": "easy",
            "topic": "git",
            "marks": 1
        },
        {
            "question_text": "What is a closure in programming?",
            "option_a": "A function that closes the program",
            "option_b": "A function with access to outer scope variables",
            "option_c": "A type of loop",
            "option_d": "A database transaction",
            "correct_option": "B",
            "difficulty_level": "hard",
            "topic": "programming concepts",
            "marks": 1
        },
        {
            "question_text": "Which of these is NOT a NoSQL database?",
            "option_a": "MongoDB",
            "option_b": "PostgreSQL",
            "option_c": "Redis",
            "option_d": "Cassandra",
            "correct_option": "B",
            "difficulty_level": "medium",
            "topic": "databases",
            "marks": 1
        },
        {
            "question_text": "What does CSS stand for?",
            "option_a": "Computer Style Sheets",
            "option_b": "Cascading Style Sheets",
            "option_c": "Creative Style System",
            "option_d": "Colorful Style Sheets",
            "correct_option": "B",
            "difficulty_level": "easy",
            "topic": "web",
            "marks": 1
        },
        {
            "question_text": "Which Big O notation represents constant time?",
            "option_a": "O(n)",
            "option_b": "O(1)",
            "option_c": "O(log n)",
            "option_d": "O(n²)",
            "correct_option": "B",
            "difficulty_level": "easy",
            "topic": "algorithms",
            "marks": 1
        },
        {
            "question_text": "In REST API, what does POST method typically do?",
            "option_a": "Retrieve data",
            "option_b": "Delete data",
            "option_c": "Create new resource",
            "option_d": "Update existing resource",
            "correct_option": "C",
            "difficulty_level": "easy",
            "topic": "web",
            "marks": 1
        }
    ]
    
    for q_data in mcq_questions:
        question = MCQQuestion(**q_data)
        db.add(question)
    
    db.commit()
    print(f"✅ Added {len(mcq_questions)} MCQ questions")


def seed_programming_problems(db: Session):
    """Add sample programming problems"""
    
    problems = [
        {
            "title": "Two Sum Problem",
            "description": """Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.""",
            "difficulty_level": "easy",
            "marks": 10,
            "input_format": "First line: space-separated integers (array)\nSecond line: target integer",
            "output_format": "Two space-separated integers representing the indices",
            "constraints": "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9\nOnly one valid answer exists",
            "sample_input": "2 7 11 15\n9",
            "sample_output": "0 1",
            "starter_code_python": """def two_sum(nums, target):
    # Your code here
    pass

# Read input
nums = list(map(int, input().split()))
target = int(input())

# Get result
result = two_sum(nums, target)
print(result[0], result[1])""",
            "starter_code_java": """import java.util.*;

public class Solution {
    public static int[] twoSum(int[] nums, int target) {
        // Your code here
        return new int[]{0, 0};
    }
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String[] input = sc.nextLine().split(" ");
        int[] nums = new int[input.length];
        for (int i = 0; i < input.length; i++) {
            nums[i] = Integer.parseInt(input[i]);
        }
        int target = sc.nextInt();
        
        int[] result = twoSum(nums, target);
        System.out.println(result[0] + " " + result[1]);
    }
}""",
            "starter_code_cpp": """#include <iostream>
#include <vector>
using namespace std;

vector<int> twoSum(vector<int>& nums, int target) {
    // Your code here
    return {0, 0};
}

int main() {
    vector<int> nums;
    int num, target;
    
    while (cin >> num) {
        nums.push_back(num);
        if (cin.peek() == '\\n') break;
    }
    cin >> target;
    
    vector<int> result = twoSum(nums, target);
    cout << result[0] << " " << result[1] << endl;
    
    return 0;
}""",
            "starter_code_javascript": """function twoSum(nums, target) {
    // Your code here
    return [0, 0];
}

// Read input (Node.js)
const input = require('fs').readFileSync('/dev/stdin', 'utf8').trim().split('\\n');
const nums = input[0].split(' ').map(Number);
const target = parseInt(input[1]);

const result = twoSum(nums, target);
console.log(result[0] + ' ' + result[1]);"""
        },
        {
            "title": "Palindrome Checker",
            "description": """Write a function to check if a given string is a palindrome.

A palindrome is a word, phrase, number, or other sequence of characters that reads the same forward and backward (ignoring spaces, punctuation, and capitalization).

Return "YES" if the string is a palindrome, "NO" otherwise.""",
            "difficulty_level": "easy",
            "marks": 10,
            "input_format": "A single line containing a string",
            "output_format": "YES or NO",
            "constraints": "1 <= string length <= 1000\nString contains only alphanumeric characters and spaces",
            "sample_input": "A man a plan a canal Panama",
            "sample_output": "YES",
            "starter_code_python": """def is_palindrome(s):
    # Your code here
    pass

# Read input
s = input().strip()

# Get result
result = is_palindrome(s)
print("YES" if result else "NO")""",
            "starter_code_java": """import java.util.*;

public class Solution {
    public static boolean isPalindrome(String s) {
        // Your code here
        return false;
    }
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();
        
        boolean result = isPalindrome(s);
        System.out.println(result ? "YES" : "NO");
    }
}""",
            "starter_code_cpp": """#include <iostream>
#include <string>
using namespace std;

bool isPalindrome(string s) {
    // Your code here
    return false;
}

int main() {
    string s;
    getline(cin, s);
    
    bool result = isPalindrome(s);
    cout << (result ? "YES" : "NO") << endl;
    
    return 0;
}""",
            "starter_code_javascript": """function isPalindrome(s) {
    // Your code here
    return false;
}

// Read input (Node.js)
const input = require('fs').readFileSync('/dev/stdin', 'utf8').trim();

const result = isPalindrome(input);
console.log(result ? 'YES' : 'NO');"""
        },
        {
            "title": "Fibonacci Sequence",
            "description": """Write a function to find the nth Fibonacci number.

The Fibonacci sequence is: 0, 1, 1, 2, 3, 5, 8, 13, 21, ...

Where each number is the sum of the two preceding ones, starting from 0 and 1.""",
            "difficulty_level": "medium",
            "marks": 10,
            "input_format": "A single integer n (the position in Fibonacci sequence)",
            "output_format": "The nth Fibonacci number",
            "constraints": "0 <= n <= 50",
            "sample_input": "10",
            "sample_output": "55",
            "starter_code_python": """def fibonacci(n):
    # Your code here
    pass

# Read input
n = int(input())

# Get result
result = fibonacci(n)
print(result)""",
            "starter_code_java": """import java.util.*;

public class Solution {
    public static long fibonacci(int n) {
        // Your code here
        return 0;
    }
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        
        long result = fibonacci(n);
        System.out.println(result);
    }
}""",
            "starter_code_cpp": """#include <iostream>
using namespace std;

long long fibonacci(int n) {
    // Your code here
    return 0;
}

int main() {
    int n;
    cin >> n;
    
    long long result = fibonacci(n);
    cout << result << endl;
    
    return 0;
}""",
            "starter_code_javascript": """function fibonacci(n) {
    // Your code here
    return 0;
}

// Read input (Node.js)
const input = parseInt(require('fs').readFileSync('/dev/stdin', 'utf8').trim());

const result = fibonacci(input);
console.log(result);"""
        }
    ]
    
    for p_data in problems:
        problem = ProgrammingProblem(**p_data)
        db.add(problem)
    
    db.commit()
    print(f"✅ Added {len(problems)} programming problems")


def main():
    print("🌱 Seeding database with sample questions...")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if questions already exist
        existing_mcq = db.query(MCQQuestion).count()
        existing_prog = db.query(ProgrammingProblem).count()
        
        if existing_mcq > 0 or existing_prog > 0:
            print(f"⚠️  Database already has {existing_mcq} MCQ and {existing_prog} programming questions")
            response = input("Do you want to add more questions? (yes/no): ")
            if response.lower() != 'yes':
                print("Seed operation cancelled.")
                return
        
        # Seed questions
        seed_mcq_questions(db)
        seed_programming_problems(db)
        
        print("\n✅ Database seeded successfully!")
        print(f"Total MCQ Questions: {db.query(MCQQuestion).count()}")
        print(f"Total Programming Problems: {db.query(ProgrammingProblem).count()}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()