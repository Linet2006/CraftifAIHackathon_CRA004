"""
Workplace Safety Sentinel - Synthetic Factory Video Generator
Generates a realistic 30 FPS industrial factory floor video with walking workers,
danger zone intrusion, PPE compliance/non-compliance, and moving equipment.
"""

import os
import cv2
import numpy as np
import math

def generate_synthetic_workplace_video(output_path: str, duration_sec: int = 15, fps: int = 30):
    width, height = 1280, 720
    total_frames = duration_sec * fps
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"[Video Generator] Rendering {total_frames} frames of industrial safety scenario to {output_path}...")

    # Danger Zone Polygon
    zone_poly = np.array([[420, 180], [860, 180], [920, 520], [380, 520]], np.int32)

    for f in range(total_frames):
        t = f / float(fps)
        
        # 1. Base Factory Floor (Dark Industrial Metallic Slate)
        frame = np.full((height, width, 3), (28, 32, 38), dtype=np.uint8)

        # Floor grid lines
        for y in range(0, height, 40):
            cv2.line(frame, (0, y), (width, y), (35, 42, 50), 1)
        for x in range(0, width, 50):
            cv2.line(frame, (x, 0), (x, height), (35, 42, 50), 1)

        # Safe Walkway Lane (Green tint borders)
        cv2.rectangle(frame, (60, 0), (220, height), (35, 55, 40), -1)
        cv2.line(frame, (60, 0), (60, height), (40, 180, 80), 2)
        cv2.line(frame, (220, 0), (220, height), (40, 180, 80), 2)
        cv2.putText(frame, "AUTHORIZED PEDESTRIAN LANE", (70, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 220, 120), 1)

        # 2. Hazard Zone Area (Robotic Automation Cell)
        overlay = frame.copy()
        cv2.fillPoly(overlay, [zone_poly], (20, 20, 80)) # Semi-transparent dark red fill
        cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)
        cv2.polylines(frame, [zone_poly], True, (40, 60, 220), 3)

        # Hazard striped perimeter markings
        cv2.putText(frame, "DANGER ZONE: ROBOTIC CELL (RESTRICTED)", (410, 160), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 70, 240), 2)

        # Animated Robotic Arm in Center of Danger Zone
        arm_base = (640, 360)
        cv2.circle(frame, arm_base, 24, (70, 75, 85), -1)
        cv2.circle(frame, arm_base, 10, (180, 190, 200), -1)
        
        arm_angle = math.sin(t * 1.5) * 0.8
        joint1_x = int(arm_base[0] + 90 * math.cos(arm_angle - 1.2))
        joint1_y = int(arm_base[1] + 90 * math.sin(arm_angle - 1.2))
        cv2.line(frame, arm_base, (joint1_x, joint1_y), (140, 145, 155), 8)
        cv2.circle(frame, (joint1_x, joint1_y), 12, (220, 120, 40), -1)

        end_x = int(joint1_x + 70 * math.cos(arm_angle * 1.8))
        end_y = int(joint1_y + 70 * math.sin(arm_angle * 1.8))
        cv2.line(frame, (joint1_x, joint1_y), (end_x, end_y), (200, 160, 40), 6)
        cv2.circle(frame, (end_x, end_y), 8, (40, 220, 240), -1)

        # 3. Worker 1: Safe Operator (Compliant with Hardhat & Vest, in safe lane)
        w1_y = int(100 + (t * 50) % (height - 180))
        w1_x = 140
        # Draw worker body
        cv2.circle(frame, (w1_x, w1_y), 16, (220, 200, 180), -1) # Head
        cv2.ellipse(frame, (w1_x, w1_y - 8), (17, 8), 0, 180, 360, (0, 220, 255), -1) # Yellow Hardhat
        cv2.rectangle(frame, (w1_x - 18, w1_y + 16), (w1_x + 18, w1_y + 65), (20, 180, 40), -1) # Green Safety Vest
        cv2.line(frame, (w1_x - 8, w1_y + 65), (w1_x - 8, w1_y + 105), (120, 100, 80), 5) # Legs
        cv2.line(frame, (w1_x + 8, w1_y + 65), (w1_x + 8, w1_y + 105), (120, 100, 80), 5)

        # 4. Worker 2: Intruding Worker (NO Hardhat, breaches Danger Zone!)
        # Walks from right side into danger zone, pauses inside, then exits
        cycle = t % 12.0
        if cycle < 4.0:
            w2_x = int(1050 - cycle * 120)
            w2_y = int(450 - cycle * 30)
        elif cycle < 8.0:
            # Inside danger zone
            w2_x = int(570 + math.sin(cycle * 3) * 20)
            w2_y = int(330 + math.cos(cycle * 2) * 15)
        else:
            # Exiting
            w2_x = int(570 + (cycle - 8.0) * 120)
            w2_y = int(330 + (cycle - 8.0) * 40)

        # Draw worker 2 (NO hardhat, dark hair, regular blue shirt)
        cv2.circle(frame, (w2_x, w2_y), 17, (210, 190, 175), -1) # Head
        cv2.circle(frame, (w2_x, w2_y - 6), 14, (40, 30, 25), -1) # Dark hair (NO HARDHAT)
        cv2.rectangle(frame, (w2_x - 19, w2_y + 17), (w2_x + 19, w2_y + 68), (140, 70, 50), -1) # Blue shirt (NO VEST)
        cv2.line(frame, (w2_x - 9, w2_y + 68), (w2_x - 9, w2_y + 110), (90, 80, 75), 5)
        cv2.line(frame, (w2_x + 9, w2_y + 68), (w2_x + 9, w2_y + 110), (90, 80, 75), 5)

        # 5. Forklift Equipment (Moving across lower factory aisle)
        fl_x = int(250 + (t * 70) % 950)
        fl_y = 620
        # Forklift chassis
        cv2.rectangle(frame, (fl_x, fl_y), (fl_x + 110, fl_y + 55), (20, 160, 240), -1) # Safety Orange
        cv2.circle(frame, (fl_x + 25, fl_y + 55), 14, (30, 30, 30), -1) # Wheels
        cv2.circle(frame, (fl_x + 85, fl_y + 55), 14, (30, 30, 30), -1)
        # Mast & Forks
        cv2.line(frame, (fl_x + 110, fl_y - 30), (fl_x + 110, fl_y + 55), (100, 100, 100), 5)
        cv2.line(frame, (fl_x + 110, fl_y + 45), (fl_x + 150, fl_y + 45), (160, 160, 160), 4)
        # Forklift Driver
        cv2.circle(frame, (fl_x + 55, fl_y - 5), 12, (220, 200, 180), -1)
        cv2.ellipse(frame, (fl_x + 55, fl_y - 10), (13, 6), 0, 180, 360, (0, 220, 255), -1) # Hardhat

        # Timestamp & Camera ID Overlay
        cv2.putText(frame, f"CAM-04 INDUSTRIAL NORTH CELL | {t:.1f}s | FPS: 30.0", 
                    (20, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 170, 180), 1)

        out.write(frame)

    out.release()
    print(f"[Video Generator] Finished: {output_path} ({os.path.getsize(output_path)/1024/1024:.2f} MB)")

if __name__ == "__main__":
    assets_dir = os.path.dirname(os.path.abspath(__file__))
    vid_path = os.path.join(assets_dir, "workplace_safety_demo.mp4")
    generate_synthetic_workplace_video(vid_path, duration_sec=12, fps=30)
