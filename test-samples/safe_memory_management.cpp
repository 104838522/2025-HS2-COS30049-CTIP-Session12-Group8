// Safe: Proper memory management with smart pointers
#include <iostream>
#include <memory>
#include <string>

int main() {
    auto data = std::make_unique<std::string>("Hello World");
    
    std::cout << *data << std::endl;
    
    // Memory automatically freed, no use-after-free possible
    
    return 0;
}
