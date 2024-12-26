
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* read_file_content(FILE* file) {
    fseek(file, 0, SEEK_END);
    long length = ftell(file);
    fseek(file, 0, SEEK_SET);

    char* content = malloc(length + 1);
    if (!content) {
        return NULL;  // 内存分配失败
    }
    
    fread(content, 1, length, file);
    content[length] = '\0';  // 以 NULL 结尾

    return content;
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: spj <input_file> <output_file> <answer_file>\n");
        return 2;  // 特判程序错误
    }

    FILE *fin = fopen(argv[1], "r");  // 输入文件
    FILE *fout = fopen(argv[2], "r"); // 选手输出
    FILE *fans = fopen(argv[3], "r"); // 标准答案

    if (!fin || !fout || !fans) {
        fprintf(stderr, "Failed to open files\n");
        return 2;  // 特判程序错误
    }

    char* input = read_file_content(fin);
    char* output = read_file_content(fout);

    if (!input || !output) {
        fprintf(stderr, "Memory allocation failed\n");
        free(input);
        free(output);
        return 2;  // 特判程序错误
    }

    // 比较输入与选手输出
    int result = strcmp(input, output);

    // 释放内存
    free(input);
    free(output);
    fclose(fin);
    fclose(fout);
    fclose(fans);

    return (result == 0) ? 0 : 1;  // 0: AC, 1: WA
}