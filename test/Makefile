BUILD_DIR = build

C_SOURCES = src/test.c src/foo/foo.c
C_FLAGS = -Wall -Werror -std=c11 -O3
C_INCLUDES = -Isrc/foo
CC = gcc
EXE = $(BUILD_DIR)/test

OBJECTS = $(addprefix $(BUILD_DIR)/,$(notdir $(C_SOURCES:.c=.o)))
vpath %.c $(sort $(dir $(C_SOURCES)))

all: $(BUILD_DIR) $(EXE)

$(EXE): $(OBJECTS)
	$(CC) -o $@ $(OBJECTS)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/%.o: %.c
	$(CC) -c $(C_FLAGS) $(C_INCLUDES) $< -o $@

.PHONY: clean
clean:
	rm -rf $(OBJECTS) $(EXE)