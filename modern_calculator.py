import customtkinter as ctk
import tkinter as tk # Added for tk.Menu
import math
import re

class CalculatorApp(ctk.CTk):
    MAX_HISTORY_ITEMS = 50

    def __init__(self):
        super().__init__()

        self.title("Enhanced Python Calculator")
        self.geometry("420x800") 
        self.resizable(False, False)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # State variables
        self.full_expression = ""
        self.current_entry = ""
        self.display_needs_reset = False
        self.history_log = []
        self.history_visible = False 

        self._configure_grid()
        self._create_widgets()
        self._update_display("0")
        self._update_live_preview_display() 

        # Bind keyboard events
        self.bind("<Key>", self._on_key_press)
        self.bind("<Return>", lambda event: self._on_equals_press())
        self.bind("<BackSpace>", lambda event: self._on_backspace_press())
        self.bind("<Escape>", lambda event: self._on_clear_press())

        self.bind("<KP_Enter>", lambda event: self._on_equals_press())
        self.bind("<KP_Add>", lambda event: self._on_operator_press('+'))
        self.bind("<KP_Subtract>", lambda event: self._on_operator_press('-'))
        self.bind("<KP_Multiply>", lambda event: self._on_operator_press('*'))
        self.bind("<KP_Divide>", lambda event: self._on_operator_press('/'))
        self.bind("<KP_Decimal>", lambda event: self._on_digit_press('.'))
        for i in range(10):
            self.bind(f"<KP_{i}>", lambda event, digit=str(i): self._on_digit_press(digit))

    def _configure_grid(self):
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(0, weight=2)  # Main display
        self.grid_rowconfigure(1, weight=1)  # Live preview display
        for i in range(2, 10): 
            self.grid_rowconfigure(i, weight=1) # Button rows
        self.grid_rowconfigure(10, weight=0) # History Toggle Button
        self.grid_rowconfigure(11, weight=3) # History Textbox

    def _create_widgets(self):
        # --- Main Display Screen ---
        self.display_var = ctk.StringVar()
        display_font = ctk.CTkFont(family="Arial", size=36, weight="bold")
        self.display_label = ctk.CTkLabel(
            self, textvariable=self.display_var, font=display_font, anchor="e",
            fg_color="gray20", corner_radius=8, padx=10
        )
        self.display_label.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=(15, 5))
        # Bind right-click for context menu
        self.display_label.bind("<Button-3>", self._show_display_context_menu)


        # --- Live Preview Display ---
        self.live_preview_var = ctk.StringVar()
        live_preview_font = ctk.CTkFont(family="Arial", size=16)
        self.live_preview_label = ctk.CTkLabel(
            self, textvariable=self.live_preview_var, font=live_preview_font, anchor="e",
            fg_color="gray15", corner_radius=6, padx=10
        )
        self.live_preview_label.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=(0,10))

        # --- Button Definitions ---
        button_row_offset = 2
        buttons_layout = [
            ("AC", 0, 0, 1, 1, self._on_clear_press, "action_clear"),
            ("(",  0, 1, 1, 1, lambda: self._on_parenthesis_press("("), "function"),
            (")",  0, 2, 1, 1, lambda: self._on_parenthesis_press(")"), "function"),
            ("DEL",0, 3, 1, 1, self._on_backspace_press, "action"),
            ("sin",1, 0, 1, 1, lambda: self._on_function_press("math.sin(math.radians("), "function"),
            ("cos",1, 1, 1, 1, lambda: self._on_function_press("math.cos(math.radians("), "function"),
            ("tan",1, 2, 1, 1, lambda: self._on_function_press("math.tan(math.radians("), "function"),
            ("sqrt",1,3, 1, 1, lambda: self._on_function_press("math.sqrt("), "function"),
            ("log",2, 0, 1, 1, lambda: self._on_function_press("math.log10("), "function"),
            ("ln", 2, 1, 1, 1, lambda: self._on_function_press("math.log("), "function"),
            ("^",  2, 2, 1, 1, lambda: self._on_operator_press("^"), "operator"),
            ("π",  2, 3, 1, 1, lambda: self._on_constant_press("math.pi"), "function"),
            ("7",  3, 0, 1, 1, lambda: self._on_digit_press("7"), "number"),
            ("8",  3, 1, 1, 1, lambda: self._on_digit_press("8"), "number"),
            ("9",  3, 2, 1, 1, lambda: self._on_digit_press("9"), "number"),
            ("/",  3, 3, 1, 1, lambda: self._on_operator_press("/"), "operator"),
            ("4",  4, 0, 1, 1, lambda: self._on_digit_press("4"), "number"),
            ("5",  4, 1, 1, 1, lambda: self._on_digit_press("5"), "number"),
            ("6",  4, 2, 1, 1, lambda: self._on_digit_press("6"), "number"),
            ("*",  4, 3, 1, 1, lambda: self._on_operator_press("*"), "operator"),
            ("1",  5, 0, 1, 1, lambda: self._on_digit_press("1"), "number"),
            ("2",  5, 1, 1, 1, lambda: self._on_digit_press("2"), "number"),
            ("3",  5, 2, 1, 1, lambda: self._on_digit_press("3"), "number"),
            ("-",  5, 3, 1, 1, lambda: self._on_operator_press("-"), "operator"),
            ("0",  6, 0, 1, 1, lambda: self._on_digit_press("0"), "number"),
            (".",  6, 1, 1, 1, lambda: self._on_digit_press("."), "number"),
            ("+/-",6, 2, 1, 1, self._on_plus_minus_press, "action"),
            ("+",  6, 3, 1, 1, lambda: self._on_operator_press("+"), "operator"),
            ("e",  7, 0, 1, 1, lambda: self._on_constant_press("math.e"), "function"),
            # "=" button now starts at column 1 and spans 3 columns
            ("=",  7, 1, 3, 1, self._on_equals_press, "equals"), 
        ]
        button_font = ctk.CTkFont(family="Arial", size=16, weight="bold")
        colors = {
            "number": ("gray30", "gray40"), "operator": ("#FF8C00", "#FFA500"),
            "function": ("gray40", "gray50"), "action": ("#6A5ACD", "#7B68EE"),
            "action_clear": ("#B22222", "#CD5C5C"), "equals": ("#32CD32", "#3CB371")
        }
        for text, r_idx, col, colspan, rowspan, cmd, btn_type in buttons_layout:
            grid_row = r_idx + button_row_offset
            fg_c, hover_c = colors.get(btn_type, ("gray25", "gray35"))
            text_color = "white"
            if btn_type in ["operator", "equals"]: text_color = "black"
            elif btn_type == "action_clear": text_color = "white"
            button = ctk.CTkButton(
                self, text=text, command=cmd, font=button_font, corner_radius=8,
                fg_color=fg_c, hover_color=hover_c, text_color=text_color
            )
            if text == "e": button.configure(fg_color=colors["number"][0], hover_color=colors["number"][1], text_color="white")
            if text == "DEL": button.configure(text_color="white") # Keep DEL white
            button.grid(row=grid_row, column=col, columnspan=colspan, rowspan=rowspan, sticky="nsew", padx=3, pady=3)

        # --- History Section ---
        self.history_toggle_button = ctk.CTkButton(
            self, text="History ▾", font=ctk.CTkFont(size=14, weight="bold"),
            command=self._toggle_history_visibility,
            fg_color="gray25", hover_color="gray35"
        )
        self.history_toggle_button.grid(row=10, column=0, columnspan=4, sticky="ew", padx=10, pady=(10,0))
        
        self.history_textbox = ctk.CTkTextbox(
            self, height=100, font=ctk.CTkFont(family="Arial", size=15),
            border_spacing=5, corner_radius=8, activate_scrollbars=True
        )
        self.history_textbox.configure(state="disabled")
        self.history_textbox.bind("<Button-1>", self._on_history_click)

    def _show_display_context_menu(self, event):
        context_menu = tk.Menu(self, tearoff=0)
        # Attempt basic styling for the tk.Menu to somewhat blend
        # These might have limited effect depending on the OS theme
        context_menu.configure(bg="#FFFFFF", fg="white", activebackground="#0078D7", activeforeground="white", relief="flat", borderwidth=0)
        
        context_menu.add_command(label="Copy", command=self._context_menu_copy_action, 
                                 background="#FFFFFF", foreground="#000000",
                                 activebackground="#0078D7", activeforeground="white")
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def _context_menu_copy_action(self):
        text_to_copy = self.display_var.get()
        self._copy_to_clipboard(text_to_copy, "Result Copied!")

    def _toggle_history_visibility(self):
        if self.history_visible:
            self.history_textbox.grid_remove()
            self.history_toggle_button.configure(text="History ▾")
            self.history_visible = False
        else:
            self.history_textbox.grid(row=11, column=0, columnspan=4, sticky="nsew", padx=10, pady=(0,10))
            self._update_history_display() 
            self.history_toggle_button.configure(text="History ▴")
            self.history_visible = True

    def _update_display(self, value=None):
        if value is not None:
            self.display_var.set(value)
        else:
            current_display_text = self.full_expression + self.current_entry
            self.display_var.set(current_display_text if current_display_text else "0")
        text_length = len(self.display_var.get())
        font_size = 36
        if text_length > 12: font_size = 30
        if text_length > 16: font_size = 24
        if text_length > 22: font_size = 20
        if text_length > 28: font_size = 16
        self.display_label.cget("font").configure(size=font_size)
        self._update_live_preview_display()

    def _update_live_preview_display(self):
        expr_to_preview = self.full_expression + self.current_entry
        if not expr_to_preview or self.display_needs_reset or \
           expr_to_preview.endswith(tuple("+-*/^")) or expr_to_preview == "-":
            self.live_preview_var.set("")
            return
        try:
            temp_expr = expr_to_preview
            open_p, closed_p = temp_expr.count('('), temp_expr.count(')')
            if open_p > closed_p: temp_expr += ')' * (open_p - closed_p)
            processed_expr = self._preprocess_for_eval(temp_expr)
            if processed_expr.count("(") != processed_expr.count(")"):
                self.live_preview_var.set("")
                return
            allowed_names = {"math": math, "__builtins__": {}}
            result = eval(processed_expr, allowed_names)
            result_str = str(int(result)) if isinstance(result, float) and result.is_integer() else f"{result:.10g}"
            if 'e' not in result_str and '.' in result_str: result_str = result_str.rstrip('0').rstrip('.')
            self.live_preview_var.set(f"≈ {result_str}")
        except Exception:
            self.live_preview_var.set("")

    def _handle_input_reset(self):
        if self.display_needs_reset:
            self.full_expression, self.current_entry, self.display_needs_reset = "", "", False

    def _on_digit_press(self, digit):
        self._handle_input_reset()
        if digit == "." and "." in self.current_entry: return
        if self.current_entry == "0" and digit != ".": self.current_entry = digit
        elif self.current_entry == "-0" and digit != ".": self.current_entry = "-" + digit
        else: self.current_entry += digit
        self._update_display()

    def _on_operator_press(self, operator):
        self._handle_input_reset()
        if self.current_entry:
            if not self.full_expression and self.current_entry == "0": self.full_expression = "0"
            elif self.current_entry == "-" and not self.full_expression: self.full_expression = "-0"
            elif self.current_entry == "-": self.full_expression += "(-0)"
            else: self.full_expression += self.current_entry
            self.full_expression += operator
            self.current_entry = ""
        elif self.full_expression:
            last_char = self.full_expression[-1]
            if last_char in "+-*/^" and not self.full_expression.endswith(("(", "s(")) and \
               not (last_char in "+-*/" and self.full_expression[-2] == '('):
                self.full_expression = self.full_expression[:-1] + operator
            else: self.full_expression += operator
        else:
            self.current_entry = "-" if operator == '-' else "0" + operator
        self.display_needs_reset = False
        self._update_display()

    def _on_function_press(self, func_template):
        self._handle_input_reset()
        if self.current_entry:
            if self.current_entry[-1].isdigit() or self.current_entry.endswith((")", "math.pi", "math.e")):
                self.full_expression += self.current_entry + "*"
            else: self.full_expression += self.current_entry
        self.full_expression += func_template
        self.current_entry = ""
        self.display_needs_reset = False
        self._update_display()

    def _on_constant_press(self, constant_str):
        self._handle_input_reset()
        if self.current_entry:
            if self.current_entry[-1].isdigit() or self.current_entry.endswith(")"):
                self.full_expression += self.current_entry + "*"
            self.current_entry = constant_str
        else: self.current_entry = constant_str
        self.display_needs_reset = False
        self._update_display()

    def _on_parenthesis_press(self, parenthesis):
        self._handle_input_reset()
        if parenthesis == "(":
            if self.current_entry:
                if self.current_entry[-1].isdigit() or self.current_entry.endswith((")", "math.pi", "math.e")):
                    self.full_expression += self.current_entry + "*"
                else: self.full_expression += self.current_entry
            self.full_expression += "("
            self.current_entry = ""
        else: # ")"
            if self.current_entry or self.full_expression.count('(') > self.full_expression.count(')'):
                if self.current_entry: self.full_expression += self.current_entry
                self.full_expression += ")"
                self.current_entry = ""
        self.display_needs_reset = False
        self._update_display()

    def _on_clear_press(self):
        self.full_expression, self.current_entry, self.display_needs_reset = "", "", True
        self._update_display("0")

    def _on_backspace_press(self):
        if self.display_needs_reset and self.current_entry: self._on_clear_press(); return
        self.display_needs_reset = False
        if self.current_entry: self.current_entry = self.current_entry[:-1]
        elif self.full_expression:
            func_endings = ["math.sin(math.radians(", "math.cos(math.radians(", "math.tan(math.radians(",
                            "math.sqrt(", "math.log10(", "math.log(", "math.pi", "math.e"]
            found = any(self.full_expression.endswith(f) for f in func_endings)
            if found:
                for f_end in func_endings:
                    if self.full_expression.endswith(f_end):
                        self.full_expression = self.full_expression[:-len(f_end)]; break
            else: self.full_expression = self.full_expression[:-1]
        self._update_display() if self.full_expression or self.current_entry else self._update_display("0")


    def _on_plus_minus_press(self):
        target_entry = ""
        is_result_negation = False

        if self.display_needs_reset and self.current_entry: 
            target_entry = self.current_entry
            is_result_negation = True
        elif self.current_entry: 
            target_entry = self.current_entry
        elif not self.full_expression or self.full_expression.endswith(tuple("+-*/^(**")):
            self.current_entry = "-" 
            self._update_display()
            return
        else: return

        if target_entry.startswith("(-") and target_entry.endswith(")"): negated_entry = target_entry[2:-1]
        elif target_entry.startswith("-"): negated_entry = target_entry[1:]
        elif target_entry != "0":
            negated_entry = f"(-{target_entry})" if target_entry.startswith("math.") or '(' in target_entry or ')' in target_entry else "-" + target_entry
        else: negated_entry = "0"

        if is_result_negation:
            self.current_entry, self.full_expression, self.display_needs_reset = negated_entry, "", False
        else: self.current_entry = negated_entry
        self._update_display()


    def _preprocess_for_eval(self, expr_str):
        processed = expr_str.replace('^', '**')
        patterns = [
            (r'(\d)([([])', r'\1*\2'), (r'(\d)(math\.)', r'\1*\2'),
            (r'(\))(\d)', r'\1*\2'), (r'(\))([([])', r'\1*\2'), (r'(\))(math\.)', r'\1*\2'),
            (r'(math\.pi|math\.e)(\d)', r'\1*\2'), (r'(math\.pi|math\.e)([([])', r'\1*\2'),
            (r'(math\.pi|math\.e)(math\.)', r'\1*\2')
        ]
        for pat, repl in patterns: processed = re.sub(pat, repl, processed)
        return processed

    def _on_equals_press(self):
        if self.display_needs_reset and not self.current_entry and not self.full_expression:
            if self.display_var.get() not in ["Error", "Error: Div by 0", "Error: Syntax", "Error: Parentheses"]:
                self.current_entry = self.display_var.get() 
            else: return

        final_expr = self.full_expression + self.current_entry
        original_expr_for_history = final_expr

        if not final_expr: self._update_display("0"); self.current_entry = "0"; self.display_needs_reset = True; return

        open_p, closed_p = final_expr.count('('), final_expr.count(')')
        if open_p > closed_p: final_expr += ')' * (open_p - closed_p)
        
        try:
            processed = self._preprocess_for_eval(final_expr)
            if processed.count("(") != processed.count(")"): raise SyntaxError("Mismatched parentheses")
            allowed_names = {"math": math, "__builtins__": {}}
            result = eval(processed, allowed_names)
            result_str = str(int(result)) if isinstance(result, float) and result.is_integer() else f"{result:.15g}"
            if 'e' not in result_str and '.' in result_str: result_str = result_str.rstrip('0').rstrip('.')
            
            self._update_display(result_str)
            self._add_to_history(original_expr_for_history, result_str)
            self.full_expression, self.current_entry, self.display_needs_reset = "", result_str, True
        except ZeroDivisionError: self._handle_eval_error(original_expr_for_history, "Error: Div by 0")
        except SyntaxError as e: self._handle_eval_error(original_expr_for_history, "Error: Parentheses" if "parentheses" in str(e) else "Error: Syntax")
        except (NameError, TypeError, ValueError): self._handle_eval_error(original_expr_for_history, "Error: Syntax")
        except Exception: self._handle_eval_error(original_expr_for_history, "Error")
        self._update_live_preview_display()

    def _handle_eval_error(self, expression, error_message):
        self._update_display(error_message)
        self._add_to_history(expression, error_message)
        self.full_expression, self.current_entry, self.display_needs_reset = "", "", True

    def _add_to_history(self, expression, result):
        if len(self.history_log) >= self.MAX_HISTORY_ITEMS: self.history_log.pop(0)
        self.history_log.append(f"{expression} = {result}")
        if self.history_visible: self._update_history_display() 

    def _update_history_display(self):
        self.history_textbox.configure(state="normal")
        self.history_textbox.delete("1.0", "end")
        for entry in reversed(self.history_log):
            self.history_textbox.insert("end", entry + "\n\n")
        self.history_textbox.configure(state="disabled")

    def _copy_to_clipboard(self, text_to_copy, feedback_message="Copied!"):
        if not text_to_copy or text_to_copy.startswith("Error"): 
            current_preview_val = self.live_preview_var.get()
            self.live_preview_var.set("Cannot copy error")
            self.after(1200, lambda: self.live_preview_var.set(current_preview_val if self.live_preview_var.get() == "Cannot copy error" else self.live_preview_var.get()))
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(text_to_copy)
            original_preview = self.live_preview_var.get()
            self.live_preview_var.set(feedback_message)
            self.after(1200, lambda: self.live_preview_var.set(original_preview if self.live_preview_var.get() == feedback_message else self.live_preview_var.get()))
        except Exception:
            original_preview = self.live_preview_var.get()
            self.live_preview_var.set("Copy failed")
            self.after(1200, lambda: self.live_preview_var.set(original_preview if self.live_preview_var.get() == "Copy failed" else self.live_preview_var.get()))

    def _on_history_click(self, event):
        if not self.history_log: return
        try:
            click_index_str = self.history_textbox.index(f"@{event.x},{event.y}")
            line_num_textbox = int(click_index_str.split('.')[0]) 
            if (line_num_textbox % 2) == 0: return
            history_log_display_index = (line_num_textbox - 1) // 2            
            if 0 <= history_log_display_index < len(self.history_log):
                actual_log_index = len(self.history_log) - 1 - history_log_display_index
                history_entry_string = self.history_log[actual_log_index]
                parts = history_entry_string.split(" = ", 1)
                if len(parts) == 2:
                    result_part = parts[1]
                    self._copy_to_clipboard(result_part, "Result Copied!")
        except Exception: pass 

    def _on_key_press(self, event):
        char, keysym = event.char, event.keysym
        if keysym in ["Return", "BackSpace", "Escape", "KP_Enter", "Control_L", "Control_R"] or \
           (keysym.startswith("KP_") and not char) or event.state & 0x4: # Ignore Ctrl modified keys here, handled by specific binding
             if not ( (event.state & 0x4) and (keysym.lower() == 'c') ) : # if it's not ctrl+c
                return


        if char.isdigit() or char == ".": self._on_digit_press(char)
        elif char in "+-*/^": self._on_operator_press(char)
        elif char == '(': self._on_parenthesis_press("(")
        elif char == ')': self._on_parenthesis_press(")")
        elif keysym.lower() == 's': self._on_function_press("math.sin(math.radians(")
        elif keysym.lower() == 'c': self._on_function_press("math.cos(math.radians(")
        elif keysym.lower() == 't': self._on_function_press("math.tan(math.radians(")
        elif keysym.lower() == 'l': self._on_function_press("math.log10(")
        elif keysym.lower() == 'n': self._on_function_press("math.log(")
        elif keysym.lower() == 'q': self._on_function_press("math.sqrt(")
        elif keysym.lower() == 'p': self._on_constant_press("math.pi")
        elif keysym.lower() == 'e': self._on_constant_press("math.e")
        elif keysym == "equal" and char == "=": self._on_equals_press()
        elif keysym == "plus" or (keysym == "equal" and char == "+"): self._on_operator_press("+")
        elif keysym == "minus": self._on_operator_press("-")
        elif keysym == "asterisk" or (keysym == "8" and char == "*"): self._on_operator_press("*")
        elif keysym == "slash" or (keysym == "question" and char == "/"): self._on_operator_press("/")

if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()
