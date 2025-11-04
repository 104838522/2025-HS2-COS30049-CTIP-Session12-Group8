// Safe: Proper format string usage
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    char buffer[100];
    
    if (argc > 1) {
        snprintf(buffer, sizeof(buffer), "%s", argv[1]);  // Safe format string
        printf("%s", buffer);  // Safe output
    }
    
    return 0;
}
