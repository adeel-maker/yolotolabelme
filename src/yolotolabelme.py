import os
import json
import argparse

def load_class_mapping(mapping_file):
    class_mapping = {}
    with open(mapping_file, 'r') as f:
        lines = f.readlines()
        for index, line in enumerate(lines):
            class_name = line.strip()
            class_mapping[index] = class_name
    return class_mapping

def convert_yolo_to_labelme(yolo_annotation_dir, labelme_output_dir, image_width, image_height, class_mapping, img_ext):
    os.makedirs(labelme_output_dir, exist_ok=True)

    # Iterate through YOLO(txt format) annotation files
    for yolo_annotation_file in os.listdir(yolo_annotation_dir):
        if yolo_annotation_file.endswith('.txt'):
            with open(os.path.join(yolo_annotation_dir, yolo_annotation_file), 'r') as yolo_file:  # Parse YOLO annotation
                yolo_annotations = yolo_file.readlines()

            labelme_shapes = []

            for yolo_annotation in yolo_annotations:
                annotation_parts = yolo_annotation.strip().split()
                if len(annotation_parts) == 5:  # Bounding box format
                    class_id, x_center, y_center, width, height = map(float, annotation_parts)

                    # Calculating coordinates for LabelMe bounding box and rescale coordinates to match image size
                    x1, y1 = int(x_center * image_width - (width * image_width) / 2), int(y_center * image_height - (height * image_height) / 2)
                    x2, y2 = int(x_center * image_width + (width * image_width) / 2), int(y_center * image_height + (height * image_height) / 2)

                    shape_type = 'rectangle'
                elif len(annotation_parts) > 5:  # Polygon format
                    class_id = float(annotation_parts[0])
                    polygon_points = [int(float(x)) for x in annotation_parts[1:]]
                    shape_type = 'polygon'
                else:
                    continue  # Skiping invalid annotations

                if class_id in class_mapping:
                    class_label = class_mapping[class_id]
                else:
                    class_label = 'unknown'  # Handling unknown classes

                if shape_type == 'rectangle':
                    labelme_shapes.append({
                        'label': class_label,
                        'points': [[x1, y1], [x2, y2]],  # Rectangle coordinates
                        'group_id': None,
                        'shape_type': shape_type,
                        'flags': {},
                    })
                elif shape_type == 'polygon':
                    labelme_shapes.append({
                        'label': class_label,
                        'points': [polygon_points],
                        'group_id': None,
                        'shape_type': shape_type,
                        'flags': {},
                    })

            # Create LabelMe JSON structure
            labelme_data = {
                'version': '4.5.9',
                'flags': {},
                'shapes': labelme_shapes,
                'imagePath': yolo_annotation_file.replace('.txt', img_ext),  # image filename
                'imageData': None,
                'imageHeight': image_height,  # image height
                'imageWidth': image_width,   # image width
            }

            # Writing LabelMe JSON file
            labelme_output_file = os.path.splitext(yolo_annotation_file)[0] + '.json'
            with open(os.path.join(labelme_output_dir, labelme_output_file), 'w') as labelme_file:
                json.dump(labelme_data, labelme_file, indent=2)

def main():
    # Creating argument parser
    parser = argparse.ArgumentParser(description="Convert YOLO annotations to LabelMe JSON format.")
    
    # Adding arguments
    parser.add_argument("--yolo", required=True, help="Path to the YOLO-annotation(TXT) directory.")
    parser.add_argument("--labelme", required=False, default= 'results', help="Path to the LabelMe-output(JSON) directory.")
    parser.add_argument("--width", type=int, required=False, default= 1024, help="Width of the images")
    parser.add_argument("--height", type=int, required=False, default= 1024, help="Height of the images")
    parser.add_argument("--classes", required=True, help="Path to the classes file (TXT format).")
    parser.add_argument("--img_ext", required=False, default=".jpg", help="Image file extension (e.g., .jpg, .png, etc.)")
    
    args = parser.parse_args()
    
    # output directory
    if not os.path.exists(args.labelme):
        os.makedirs(args.labelme)
    
    
    class_mapping = load_class_mapping(args.classes)
    
    
    convert_yolo_to_labelme(args.yolo, args.labelme, args.width, args.height, class_mapping, args.img_ext)


    print("-------------------------Conversion completed------------------------------")
    
if __name__ == '__main__':
    main()
