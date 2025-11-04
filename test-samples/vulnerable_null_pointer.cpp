// Vulnerable: Null pointer dereference
#include <iostream>
#include <cstring>

class User {
public:
    char name[50];
    void printName() {
        std::cout << "User: " << name << std::endl;
    }
};

int main() {
    User *user = nullptr;
    
    // Vulnerable: dereferencing null pointer
    strcpy(user->name, "John");
    user->printName();
    
    return 0;
}
