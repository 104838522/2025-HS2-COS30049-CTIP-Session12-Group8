// Vulnerable: Buffer overflow with strcpy
#include <stdio.h>
#include <string.h>

int main() {
    char buffer[10];
    char input[50];
    
    printf("Enter your name: ");
    gets(input);  // Dangerous: no bounds checking
    
    strcpy(buffer, input);  // Buffer overflow risk
    
    printf("Hello, %s\n", buffer);
    return 0;
}
