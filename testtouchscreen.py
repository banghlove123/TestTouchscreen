import tkinter as tk
import math

BOX_SIZE = 20
BOX_HIT_RADIUS = 15
TOLERANCE = 30  # สำหรับความแม่นยำเส้นเป้าหมาย


class TouchTestApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True)
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        self.cx, self.cy = self.w // 2, self.h // 2
        self.passed_all_boxes = False

        self.canvas = tk.Canvas(root, width=self.w, height=self.h, bg="white")
        self.canvas.pack()

        self.boxes = []  # เก็บตำแหน่งและ object ของกล่องทั้งหมด

        self.draw_border()
        self.draw_x_cross()
        self.draw_target_boxes()

        self.line_start = (100, 100)
        self.line_end = (self.w - 100, self.h - 100)
        # self.canvas.create_line(*self.line_start, *self.line_end, fill="blue", width=10, dash=(6, 4))

        self.path = []
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_line)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        root.bind("<Escape>", lambda e: root.destroy())

    def draw_border(self):
        border_thickness = 10
        # วาดกรอบสีดำ
        self.canvas.create_rectangle(0, 0, self.w, border_thickness, fill="black")
        self.canvas.create_rectangle(
            0, self.h - border_thickness, self.w, self.h, fill="black"
        )
        self.canvas.create_rectangle(0, 0, border_thickness, self.h, fill="black")
        self.canvas.create_rectangle(
            self.w - border_thickness, 0, self.w, self.h, fill="black"
        )

    def draw_x_cross(self):
        # เปลี่ยนกากบาทแนวตั้ง/แนวนอน เป็นเส้น X
        self.diag1 = self.canvas.create_line(
            0, 0, self.w, self.h, fill="red", width=4, tags="cross"
        )
        self.diag2 = self.canvas.create_line(
            self.w, 0, 0, self.h, fill="red", width=4, tags="cross"
        )

    def draw_target_boxes(self):
        step = 20

        # รอบขอบจอ
        for x in range(0, self.w, step):
            self.create_box(x, 0)  # Top
            self.create_box(x, self.h - 1)  # Bottom
        for y in range(0, self.h, step):
            self.create_box(0, y)  # Left
            self.create_box(self.w - 1, y)  # Right

        # ตามเส้นกากบาทตัว X
        for i in range(0, self.w, step):
            # เส้นทแยง ↘
            y1 = int((i / self.w) * self.h)
            self.create_box(i, y1)

            # เส้นทแยง ↙
            y2 = int(((self.w - i) / self.w) * self.h)
            self.create_box(i, y2)

    def create_box(self, x, y):
        half = BOX_SIZE // 2
        box = self.canvas.create_rectangle(
            x - half, y - half, x + half, y + half, fill="red", outline="red"
        )
        self.boxes.append({"id": box, "x": x, "y": y, "hit": False})

    def start_draw(self, event):
        self.canvas.delete("userline")
        self.canvas.delete("score")
        self.path = []

        # Reset box colors
        for box in self.boxes:
            self.canvas.itemconfig(box["id"], fill="red")
            box["hit"] = False

    def draw_line(self, event):
        if self.path:
            last = self.path[-1]
            self.canvas.create_line(
                last[0], last[1], event.x, event.y, fill="black", tags="userline"
            )
        self.path.append((event.x, event.y))

        # ตรวจว่าลากผ่าน box ไหน → เปลี่ยนเป็นเขียว
        for box in self.boxes:
            if not box["hit"]:
                if (
                    self.distance(event.x, event.y, box["x"], box["y"])
                    <= BOX_HIT_RADIUS
                ):
                    self.canvas.itemconfig(box["id"], fill="green")
                    box["hit"] = True
        # ตรวจว่าลากผ่านกล่องไหนแล้วเปลี่ยนสี


        for box in self.boxes:
            if not box["hit"]:
                if self.distance(event.x, event.y, box["x"], box["y"]) <= BOX_HIT_RADIUS:
                    self.canvas.itemconfig(box["id"], fill="green")
                    box["hit"] = True

        # 🔍 ตรวจว่าทุกกล่องถูกลากผ่านหรือยัง
        if not self.passed_all_boxes:
            if all(box["hit"] for box in self.boxes):
                self.passed_all_boxes = True
                self.canvas.create_text(
                    self.cx,
                    100,
                    text="ผ่านการทดสอบแล้ว !",
                    fill="green",
                    font=("Arial", 28, "bold"),
                    tags="score",
                )

    def end_draw(self, event):
        # accuracy = self.calculate_accuracy()
        # self.canvas.create_text(
        #     self.cx,
        #     50,
        #     text=f"ความแม่นยำ: {accuracy:.2f}%",
        #     fill="green",
        #     font=("Arial", 24, "bold"),
        #     tags="score",
        # )
        pass

    def calculate_accuracy(self):
        total = len(self.path)
        if total == 0:
            return 0.0
        match = 0
        for x, y in self.path:
            dist = self.point_to_line_distance((x, y), self.line_start, self.line_end)
            if dist <= TOLERANCE:
                match += 1
        return (match / total) * 100

    def point_to_line_distance(self, pt, line_start, line_end):
        x0, y0 = pt
        x1, y1 = line_start
        x2, y2 = line_end
        num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        den = math.hypot(x2 - x1, y2 - y1)
        return num / den if den != 0 else float("inf")

    def distance(self, x1, y1, x2, y2):
        return math.hypot(x1 - x2, y1 - y2)


# เริ่มโปรแกรม
if __name__ == "__main__":

    root = tk.Tk()
    app = TouchTestApp(root)
    root.mainloop()
