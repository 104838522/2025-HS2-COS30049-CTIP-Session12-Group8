// Safe: Proper bounds checking
#include <stdio.h>
#include <string.h>

int main() {
    char buffer[10];
    char input[50];
    
    printf("Enter your name: ");
    if (fgets(input, sizeof(input), stdin) != NULL) {
        // Remove newline
        input[strcspn(input, "\n")] = 0;
        
        // Safe copy with bounds checking
        strncpy(buffer, input, sizeof(buffer) - 1);
        buffer[sizeof(buffer) - 1] = '\0';
        
        printf("Hello, %s\n", buffer);
    }
    return 0;
}
