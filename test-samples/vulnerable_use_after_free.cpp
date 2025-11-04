// Vulnerable: Use-after-free
#include <iostream>
#include <cstring>

int main() {
    char *data = new char[20];
    strcpy(data, "Hello World");
    
    delete[] data;
    
    // Vulnerable: using freed memory
    std::cout << data << std::endl;
    
    return 0;
}
