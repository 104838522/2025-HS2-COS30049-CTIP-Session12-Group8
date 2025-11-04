// Vulnerable: Format string vulnerability
#include <stdio.h>

int main(int argc, char *argv[]) {
    char buffer[100];
    
    if (argc > 1) {
        sprintf(buffer, argv[1]);  // Dangerous: user controls format string
        printf(buffer);  // Format string vulnerability
    }
    
    return 0;
}
