import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import math
import re

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    HAS_PLOT_LIBS = True
except ImportError:
    HAS_PLOT_LIBS = False

class AdvancedCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Advenced Calculator")
        self.geometry("400x600") 
        self.minsize(380, 550)
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.expression = ""
        self.memory_value = 0
        self.is_degree = True
        self.history_log = []
        self.result_var = ctk.StringVar(value="0")
        self.equation_var = ctk.StringVar(value="")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Display Row
        self.grid_rowconfigure(1, weight=1) # Tabs Row

        self._create_display_area()
        self._create_tabs()
        self._bind_keys()

    def _create_display_area(self):
        self.display_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.display_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))

        self.lbl_equation = ctk.CTkLabel(
            self.display_frame, textvariable=self.equation_var,
            font=("Roboto", 14), text_color="gray60", anchor="e"
        )
        self.lbl_equation.pack(fill="x", pady=(0, 2))

        self.entry_result = ctk.CTkEntry(
            self.display_frame, textvariable=self.result_var,
            font=("Roboto Medium", 40), justify="right",
            border_width=0, fg_color="transparent", text_color="white"
        )
        self.entry_result.pack(fill="x")
        
        ctk.CTkFrame(self.display_frame, height=2, fg_color="#1f6aa5").pack(fill="x", pady=5)

    def _create_tabs(self):
        self.tabview = ctk.CTkTabview(self, width=380, command=self._on_tab_change)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=5, pady=0)
        
        self.tab_calc = self.tabview.add("Calculator")
        self.tab_plot = self.tabview.add("Graphing")
        
        self._setup_calculator_tab()
        self._setup_graphing_tab()

    def _on_tab_change(self):
        # Hides the calculator display when in Graphing mode
        if self.tabview.get() == "Graphing":
            self.display_frame.grid_remove()
        else:
            self.display_frame.grid()
            # FIX: Remove focus from plot entry so it doesn't receive input in background
            self.focus_set()

    def _setup_calculator_tab(self):
        self.tab_calc.columnconfigure((0,1,2,3,4), weight=1)
        for i in range(10): self.tab_calc.rowconfigure(i, weight=1) 
        
        top_frame = ctk.CTkFrame(self.tab_calc, fg_color="transparent")
        top_frame.grid(row=0, column=0, columnspan=5, sticky="ew", pady=(0, 5))
        
        self.deg_switch = ctk.CTkSwitch(top_frame, text="DEG", onvalue=True, offvalue=False)
        self.deg_switch.select()
        self.deg_switch.pack(side="left", padx=5)

        ctk.CTkButton(top_frame, text="AC", width=40, fg_color="#B22222", 
                      command=lambda: self._on_input("AC")).pack(side="right", padx=2)
        
        ctk.CTkButton(top_frame, text="?", width=30, fg_color="#607D8B", 
                      command=self._open_help_window).pack(side="right", padx=2)

        ctk.CTkButton(top_frame, text="Hist", width=40, fg_color="#455A64", 
                      command=self._open_history_window).pack(side="right", padx=2)

        sci_buttons = [
            ("sin", "math.sin("), ("cos", "math.cos("), ("tan", "math.tan("), ("√", "math.sqrt("), ("^", "**"),
            ("sinh", "math.sinh("), ("cosh", "math.cosh("), ("tanh", "math.tanh("), ("ln", "math.log("), ("log", "math.log10("),
            ("asin", "math.asin("), ("acos", "math.acos("), ("atan", "math.atan("), ("e", "math.e"), ("π", "math.pi"),
            ("gcd", "math.gcd("), ("lcm", "math.lcm("), ("nCr", "math.comb("), ("nPr", "math.perm("), ("n!", "math.factorial(")
        ]

        row_offset = 1
        col_count = 5
        for i, (txt, val) in enumerate(sci_buttons):
            r = row_offset + (i // col_count)
            c = i % col_count
            self._btn(self.tab_calc, txt, r, c, "gray25", font_size=14, cmd=lambda v=val: self._on_input_raw(v))

        sep_row = row_offset + (len(sci_buttons) // col_count)
        ctk.CTkFrame(self.tab_calc, height=2, fg_color="gray30").grid(row=sep_row, column=0, columnspan=5, sticky="ew", pady=10)

        main_buttons = [
            ("(", 0), (")", 1), ("%", 2), ("abs", 3), ("÷", 4),
            ("7", 0), ("8", 1), ("9", 2), (",", 3), ("×", 4),
            ("4", 0), ("5", 1), ("6", 2), ("1/x", 3), ("-", 4),
            ("1", 0), ("2", 1), ("3", 2), ("x²", 3), ("+", 4),
            ("0", 0, 2), (".", 2), ("Ans", 3), ("=", 4)
        ]

        base_row = sep_row + 1
        for item in main_buttons:
            txt, c = item[0], item[1]
            r_idx = list(main_buttons).index(item) // 5
            r = base_row + r_idx
            
            if txt in ["=", "AC"]: color = "#32CD32" if txt == "=" else "#B22222"
            elif txt in ["÷", "×", "-", "+"]: color = "#FF8C00"
            elif txt.isdigit() or txt == ".": color = "gray20"
            else: color = "gray30"

            colspan = item[2] if len(item) > 2 else 1
            
            if txt == "x²": cmd = lambda: self._on_input_raw("**2")
            elif txt == "1/x": cmd = lambda: self._on_input_raw("**-1")
            elif txt == "Ans": cmd = lambda: self._on_input("Ans")
            elif txt == "abs": cmd = lambda: self._on_input_raw("abs(")
            elif txt == ",": cmd = lambda: self._on_input_raw(",")
            else: cmd = lambda x=txt: self._on_input(x)

            self._btn(self.tab_calc, txt, r, c, color, colspan=colspan, font_size=24, cmd=cmd)

    def _setup_graphing_tab(self):
        if not HAS_PLOT_LIBS:
            ctk.CTkLabel(self.tab_plot, text="Matplotlib is not installed.", text_color="red").pack(pady=20)
            return

        input_frame = ctk.CTkFrame(self.tab_plot, fg_color="transparent")
        input_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(input_frame, text="y =").pack(side="left", padx=2)
        self.plot_entry = ctk.CTkEntry(input_frame, placeholder_text="e.g. sin(x)")
        self.plot_entry.pack(side="left", fill="x", expand=True, padx=2)
        
        ctk.CTkButton(input_frame, text="Plot", width=50, fg_color="#32CD32", command=self._plot_graph).pack(side="right", padx=2)

        helper_frame = ctk.CTkFrame(self.tab_plot)
        helper_frame.pack(fill="x", padx=5, pady=2)
        
        helpers = [
            "x", "sin", "cos", "tan", "log", "ln",
            "(", ")", "e", "π", "^", "√",
            "+", "-", "*", "/", "abs", "sinh",
            "cosh", "tanh", "asin", "acos", "atan", "1/x"
        ]
        
        columns = 6
        for i, h in enumerate(helpers):
            btn = ctk.CTkButton(helper_frame, text=h, width=40, height=35, fg_color="gray30",
                                font=("Arial", 12),
                                command=lambda t=h: self._insert_plot_token(t))
            btn.grid(row=i//columns, column=i%columns, padx=2, pady=2, sticky="ew")
        
        for i in range(columns): helper_frame.columnconfigure(i, weight=1)

        self.plot_frame = ctk.CTkFrame(self.tab_plot)
        self.plot_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def _btn(self, parent, text, r, c, color, colspan=1, font_size=20, cmd=None):
        ctk.CTkButton(
            parent, text=text, font=("Arial", font_size, "bold"),
            fg_color=color, hover_color=self._adjust_color(color),
            command=cmd, corner_radius=8
        ).grid(row=r, column=c, columnspan=colspan, sticky="nsew", padx=3, pady=3)

    def _open_help_window(self):
        help_win = ctk.CTkToplevel(self)
        help_win.title("User Guide")
        help_win.geometry("400x500")
        help_win.attributes("-topmost", True)

        lbl_title = ctk.CTkLabel(help_win, text="Math Operations Guide", font=("Arial", 20, "bold"))
        lbl_title.pack(pady=10)

        textbox = ctk.CTkTextbox(help_win, font=("Tahoma", 14), text_color="white")
        textbox.pack(fill="both", expand=True, padx=10, pady=10)

        help_text = """
        • Multi-input Functions:
          For functions like gcd, lcm, nCr, and nPr, use a comma (,) to separate numbers.
          
          Example Combination (choose 2 from 5):
          nCr(5, 2)  --> Result: 10
          
          Example GCD:
          gcd(12, 18) --> Result: 6

        • DEG Button:
          If enabled (checked), trigonometric inputs (sin, cos, ...) are treated as Degrees.
          If disabled, they are treated as Radians.
          
        • Graphing:
          In the Graphing tab, the variable must be 'x'.
          Example: sin(x) * x
          
        • Hyperbolic Functions:
          sinh, cosh, tanh and their inverses are available for engineering calculations.
        """
        textbox.insert("0.0", help_text)
        textbox.configure(state="disabled")

    def _open_history_window(self):
        hist_win = ctk.CTkToplevel(self)
        hist_win.title("History")
        hist_win.geometry("350x500")
        hist_win.attributes("-topmost", True)

        lbl_title = ctk.CTkLabel(hist_win, text="Calculation History", font=("Arial", 18, "bold"))
        lbl_title.pack(pady=5)

        textbox = ctk.CTkTextbox(hist_win, font=("Consolas", 14), text_color="white")
        textbox.pack(fill="both", expand=True, padx=10, pady=5)

        if not self.history_log:
            textbox.insert("0.0", "No history available.")
        else:
            full_log = "\n".join(self.history_log)
            textbox.insert("0.0", full_log)
        
        textbox.configure(state="disabled")

    def _on_input(self, char):
        if char == "AC":
            self.expression = ""
            self.result_var.set("0")
            self.equation_var.set("")
        elif char == "Ans":
             if self.memory_value != 0:
                 self.expression += str(self.memory_value)
                 self.result_var.set(self.expression)
        elif char == "=":
            self._calculate()
        elif char in ["×", "÷"]:
            self.expression += "*" if char == "×" else "/"
            self.result_var.set(self.expression)
        elif char == "%":
             self.expression += "/100"
             self._calculate()
        else:
            self.expression += char
            self.result_var.set(self.expression)

    def _on_input_raw(self, text):
        self.expression += text
        self.result_var.set(self.expression)

    def _insert_plot_token(self, token):
        if token == "^": token = "**"
        elif token == "√": token = "sqrt("
        elif token == "1/x": token = "**-1"
        elif token in ["sin", "cos", "tan", "sinh", "cosh", "tanh", "asin", "acos", "atan", "log", "ln", "abs"]: 
            token += "("
        
        self.plot_entry.insert(tk.INSERT, token)
        self.plot_entry.focus_set()

    def _auto_close_parentheses(self, expr_str):
        open_p = expr_str.count("(")
        close_p = expr_str.count(")")
        if open_p > close_p:
            return expr_str + ")" * (open_p - close_p)
        return expr_str

    def _calculate(self):
        original = self.expression
        if not original: return

        try:
            safe_env = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
            safe_env.update({"abs": abs, "round": round})
            
            expr = original
            if self.deg_switch.get(): 
                for func in ["sin", "cos", "tan"]:
                     expr = re.sub(r'(?<![a-zA-Z_])math\.(sin|cos|tan)\(', r'math.\1(math.radians(', expr)

            expr = self._auto_close_parentheses(expr)

            res = eval(expr, {"__builtins__": None}, safe_env)
            
            self.memory_value = res

            if isinstance(res, (int, float)):
                res_str = f"{res:g}" 
            else:
                res_str = str(res)

            self.result_var.set(res_str)
            self.equation_var.set(original + " =")
            
            self.history_log.append(f"{original} = {res_str}")
            
            self.expression = res_str
            
        except Exception as e:
            self.result_var.set("Error")

    def _plot_graph(self):
        if not HAS_PLOT_LIBS: return
        func = self.plot_entry.get()
        if not func: return

        for widget in self.plot_frame.winfo_children(): widget.destroy()

        try:
            x = np.linspace(-10, 10, 500)
            safe_np = {
                "x": x, "np": np, 
                "sin": np.sin, "cos": np.cos, "tan": np.tan,
                "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
                "asin": np.arcsin, "acos": np.arccos, "atan": np.arctan,
                "sqrt": np.sqrt, "abs": np.abs, 
                "log": np.log10, "ln": np.log, 
                "pi": np.pi, "e": np.e
            }
            func_ready = func.replace("^", "**")
            
            func_ready = self._auto_close_parentheses(func_ready)

            y = eval(func_ready, {"__builtins__": None}, safe_np)

            fig, ax = plt.subplots(figsize=(3, 2.5), dpi=100)
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#1a1a1a')
            
            ax.plot(x, y, color='#00ff88', linewidth=1.5)
            ax.grid(True, color='gray', linestyle=':', alpha=0.3)
            ax.axhline(y=0, color='white', linewidth=0.5)
            ax.axvline(x=0, color='white', linewidth=0.5)
            ax.tick_params(colors='gray', labelsize=8)
            for spine in ax.spines.values(): spine.set_visible(False)

            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Error", "Invalid Equation")

    def _adjust_color(self, hex_color):
        return "gray50" if hex_color.startswith("#") else "gray35"

    def _bind_keys(self):
        self.bind("<Return>", lambda e: self._calculate())
        self.bind("<KP_Enter>", lambda e: self._calculate())
        self.bind("<Escape>", lambda e: self._on_input("AC"))
        self.bind("<BackSpace>", lambda e: self._on_backspace())
        
        for key in "0123456789.+-*/^%()":
            self.bind(key, lambda e, k=key: self._safe_input(k))

    def _safe_input(self, char):
        if self.tabview.get() == "Graphing":
            return
        self._on_input(char)

    def _on_backspace(self):
        if self.tabview.get() == "Graphing":
            return

        self.expression = self.expression[:-1]
        self.result_var.set(self.expression if self.expression else "0")

if __name__ == "__main__":
    app = AdvancedCalculator()
    app.mainloop()