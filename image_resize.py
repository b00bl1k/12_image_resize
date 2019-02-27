import argparse
import os
import sys
from PIL import Image


PROPORTION_ERR_MIN = 0.1


def get_target_filename(source, target, width, height):
    if target:
        return target
    root, ext = os.path.splitext(source)
    return "{}__{}x{}{}".format(root, width, height, ext)


def calculate_new_size(src_width, src_height, dst_width, dst_height, scale):
    src_prop = src_width / src_height
    if scale:
        new_width = int(src_width * scale)
        new_height = int(src_height * scale)
    elif dst_width is None:
        new_width = int(dst_width * src_prop)
        new_height = dst_width
    elif dst_height is None:
        new_width = dst_width
        new_height = int(dst_width / src_prop)
    else:
        new_width = dst_width
        new_height = dst_height

    return new_width, new_height


def is_proportional(src_width, src_height, new_width, new_height):
    src_prop = src_width / src_height
    new_prop = new_width / new_height
    return abs(src_prop - new_prop) < PROPORTION_ERR_MIN


def parse_args():
    parser = argparse.ArgumentParser(description="Image resizer.")
    parser.add_argument("source", help="Path to the source image")
    parser.add_argument(
        "target",
        nargs="?",
        help="Path to the output image"
    )
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--scale", type=float)

    args = parser.parse_args()

    if args.scale is not None and args.scale <= 0:
        parser.error("Invalid value of scale argument")

    if args.width is not None and args.width <= 0:
        parser.error("Invalid value of width option")

    if args.height is not None and args.height <= 0:
        parser.error("Invalid value of height option")

    if args.scale is not None and (args.width is not None or
                                   args.height is not None):
        parser.error("Width/height and scale is exclusive options")

    if not any((args.scale, args.width, args.height)):
        parser.error("No resize options specified")

    return args


def main():
    try:
        args = parse_args()
        src_img = Image.open(args.source)
        src_width, src_height = src_img.size
        new_width, new_height = calculate_new_size(
            src_width,
            src_height,
            args.width,
            args.height,
            args.scale
        )
        if not is_proportional(src_width, src_height, new_width, new_height):
            print("Warning: target image is not proportional to source")
        new_img = src_img.resize((new_width, new_height))
        src_img.close()
        target_filename = get_target_filename(
            args.source,
            args.target,
            src_width,
            src_height
        )
        new_img.save(target_filename)
    except FileNotFoundError:
        sys.exit("The source image not found")
    except OSError:
        sys.exit("The source is not valid image file")


if __name__ == "__main__":
    main()
