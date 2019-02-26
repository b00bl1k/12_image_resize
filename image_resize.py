import argparse
import os
import sys
from PIL import Image


PROPORTION_ERR_MIN = 0.1


def get_target_filename(source, target, size):
    if target:
        return target
    root, ext = os.path.splitext(source)
    return "{}__{}x{}{}".format(root, *size, ext)


def resize_image(source, new_size, scale):
    im = Image.open(source)
    origin_width, origin_height = im.size
    origin_prop = origin_width / origin_height

    if scale:
        new_width = int(origin_width * scale)
        new_height = int(origin_height * scale)
    elif new_size[0] is None:
        new_width = int(new_size[1] * origin_prop)
        new_height = new_size[1]
    elif new_size[1] is None:
        new_width = new_size[0]
        new_height = int(new_size[0] / origin_prop)
    else:
        new_width, new_height = new_size
        new_prop = new_width / new_height
        if abs(new_prop - origin_prop) > PROPORTION_ERR_MIN:
            print("Warning: new image is not same proportion")

    new_image = im.resize((new_width, new_height))
    im.close()

    return new_image


def parse_args():
    parser = argparse.ArgumentParser(description="Image resizer.")
    parser.add_argument("source", help='Path to the source image')
    parser.add_argument(
        "target",
        nargs="?",
        help="Path to the output image"
    )
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--scale", type=float)

    args = parser.parse_args()

    if args.scale and args.scale <= 0:
        raise ValueError("Invalid value of scale argument")

    if bool(args.scale) == (bool(args.width) or bool(args.height)):
        raise ValueError("Width/height or scale must be specified")

    return args


def main():
    try:
        args = parse_args()
        img = resize_image(
            args.source,
            (args.width, args.height),
            args.scale
        )
        target_filename = get_target_filename(
            args.source,
            args.target,
            img.size
        )
        img.save(target_filename)
    except FileNotFoundError:
        sys.exit("The source image not found")
    except OSError:
        sys.exit("The source is not valid image file")
    except ValueError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
