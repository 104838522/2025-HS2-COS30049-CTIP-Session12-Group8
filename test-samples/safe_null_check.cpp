// Safe: Proper null pointer checking
#include <iostream>
#include <string>
#include <memory>

class User {
public:
    std::string name;
    void printName() {
        std::cout << "User: " << name << std::endl;
    }
};

int main() {
    std::unique_ptr<User> user = std::make_unique<User>();
    
    // Safe: pointer is guaranteed to be valid
    if (user) {
        user->name = "John";
        user->printName();
    }
    
    return 0;
}
