"""Convert various annotation formats to YOLO format.

Supports conversion from:
- CCPD format (filename encoded)
- XML (PASCAL VOC style)
- JSON (COCO style)

Output: YOLO format text files (one per image)
Format: <class_id> <x_center> <y_center> <width> <height> (normalized 0-1)
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple
import argparse


def parse_ccpd_filename(filename: str, img_w: int, img_h: int) -> Tuple[int, int, int, int]:
    """Parse CCPD filename to extract bbox coordinates.
    
    CCPD filename format: area-x1_y1_x2_y2-...-platetext.jpg
    Returns: (x1, y1, x2, y2) in pixels
    """
    parts = filename.split('-')
    if len(parts) < 3:
        raise ValueError(f"Invalid CCPD filename: {filename}")
    
    bbox_str = parts[2]  # typically third part contains bbox
    coords = bbox_str.split('_')
    if len(coords) == 4:
        x1, y1, x2, y2 = map(int, coords)
        return x1, y1, x2, y2
    else:
        # fallback parsing if different encoding
        raise ValueError(f"Could not parse bbox from {filename}")


def bbox_to_yolo(x1: int, y1: int, x2: int, y2: int, img_w: int, img_h: int) -> Tuple[float, float, float, float]:
    """Convert pixel bbox to YOLO normalized format."""
    x_center = ((x1 + x2) / 2.0) / img_w
    y_center = ((y1 + y2) / 2.0) / img_h
    width = (x2 - x1) / img_w
    height = (y2 - y1) / img_h
    return x_center, y_center, width, height


def convert_xml_to_yolo(xml_path: Path, img_w: int, img_h: int, class_name: str = "plate") -> List[str]:
    """Convert PASCAL VOC XML annotation to YOLO format lines."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    lines = []
    for obj in root.findall("object"):
        name_elem = obj.find("name")
        if name_elem is None or name_elem.text is None:
            continue
        name = name_elem.text
        if name.lower() != class_name.lower():
            continue  # skip non-plate objects
        
        bbox = obj.find("bndbox")
        if bbox is None:
            continue
            
        xmin_elem = bbox.find("xmin")
        ymin_elem = bbox.find("ymin")
        xmax_elem = bbox.find("xmax")
        ymax_elem = bbox.find("ymax")
        
        # Type-safe None checks for XML elements
        if not all([xmin_elem is not None, ymin_elem is not None, 
                    xmax_elem is not None, ymax_elem is not None]):
            continue
        
        # Now we can safely assert these are not None
        assert xmin_elem is not None and xmin_elem.text is not None
        assert ymin_elem is not None and ymin_elem.text is not None
        assert xmax_elem is not None and xmax_elem.text is not None
        assert ymax_elem is not None and ymax_elem.text is not None
            
        x1 = int(xmin_elem.text)
        y1 = int(ymin_elem.text)
        x2 = int(xmax_elem.text)
        y2 = int(ymax_elem.text)
        
        xc, yc, w, h = bbox_to_yolo(x1, y1, x2, y2, img_w, img_h)
        lines.append(f"0 {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}")
    
    return lines


def convert_ccpd_batch(images_dir: Path, output_labels_dir: Path):
    """Convert CCPD images (filename encoded) to YOLO labels."""
    output_labels_dir.mkdir(parents=True, exist_ok=True)
    
    import cv2
    for img_path in images_dir.glob("*.jpg"):
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        h, w = img.shape[:2]
        
        try:
            x1, y1, x2, y2 = parse_ccpd_filename(img_path.name, w, h)
            xc, yc, bw, bh = bbox_to_yolo(x1, y1, x2, y2, w, h)
            label_line = f"0 {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n"
            
            label_path = output_labels_dir / (img_path.stem + ".txt")
            with open(label_path, "w", encoding="utf-8") as f:
                f.write(label_line)
        except Exception as e:
            print(f"Warning: failed to parse {img_path.name}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Convert annotations to YOLO format")
    parser.add_argument("--format", choices=["ccpd", "xml", "json"], required=True,
                        help="Source annotation format")
    parser.add_argument("--images-dir", type=Path, required=True,
                        help="Directory containing images")
    parser.add_argument("--annotations-dir", type=Path,
                        help="Directory containing annotation files (for xml/json)")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Output directory for YOLO format labels")
    parser.add_argument("--class-name", type=str, default="plate",
                        help="Class name to filter (default: plate)")
    
    args = parser.parse_args()
    
    if args.format == "ccpd":
        convert_ccpd_batch(args.images_dir, args.output_dir)
        print(f"Converted CCPD annotations to {args.output_dir}")
    
    elif args.format == "xml":
        if not args.annotations_dir:
            raise ValueError("--annotations-dir required for XML format")
        
        args.output_dir.mkdir(parents=True, exist_ok=True)
        import cv2
        
        for xml_path in args.annotations_dir.glob("*.xml"):
            img_path = args.images_dir / (xml_path.stem + ".jpg")
            if not img_path.exists():
                img_path = args.images_dir / (xml_path.stem + ".png")
            
            if img_path.exists():
                img = cv2.imread(str(img_path))
                if img is None:
                    print(f"Warning: Could not read image {img_path}")
                    continue
                h, w = img.shape[:2]
                lines = convert_xml_to_yolo(xml_path, w, h, args.class_name)
                
                if lines:
                    label_path = args.output_dir / (xml_path.stem + ".txt")
                    with open(label_path, "w", encoding="utf-8") as f:
                        f.write("\n".join(lines) + "\n")
        
        print(f"Converted XML annotations to {args.output_dir}")
    
    else:
        print(f"Format {args.format} conversion not yet implemented. Extend this script as needed.")


if __name__ == "__main__":
    main()
