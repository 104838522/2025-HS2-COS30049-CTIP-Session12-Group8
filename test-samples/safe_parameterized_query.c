// Safe: Parameterized query (simulated)
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int isValidUsername(const char *username) {
    for (int i = 0; username[i]; i++) {
        if (!isalnum(username[i]) && username[i] != '_') {
            return 0;
        }
    }
    return 1;
}

void executeQuery(const char *username) {
    if (!isValidUsername(username)) {
        printf("Invalid username format\n");
        return;
    }
    
    // Safe: using parameterized query placeholder
    printf("Executing: SELECT * FROM users WHERE name = ? [param: %s]\n", username);
    // In real code, this would use prepared statements
}

int main() {
    char username[100];
    
    printf("Enter username: ");
    scanf("%99s", username);
    
    executeQuery(username);
    
    return 0;
}
