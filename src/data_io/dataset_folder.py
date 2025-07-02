

# import cv2
# import torch
# from torchvision import datasets
# import numpy as np


# def opencv_loader(path):
#     img = cv2.imread(path)
#     return img


# class DatasetFolderFT(datasets.ImageFolder):
#     def __init__(self, root, transform=None, target_transform=None,
#                  ft_width=10, ft_height=10, loader=opencv_loader):
#         super(DatasetFolderFT, self).__init__(root, transform, target_transform, loader)
#         self.root = root
#         self.ft_width = ft_width
#         self.ft_height = ft_height

#     def __getitem__(self, index):
#         path, target = self.samples[index]
#         sample = self.loader(path)
#         # generate the FT picture of the sample
#         ft_sample = generate_FT(sample)
#         if sample is None:
#             print('image is None --> ', path)
#         if ft_sample is None:
#             print('FT image is None -->', path)
#         assert sample is not None

#         ft_sample = cv2.resize(ft_sample, (self.ft_width, self.ft_height))
#         ft_sample = torch.from_numpy(ft_sample).float()
#         ft_sample = torch.unsqueeze(ft_sample, 0)

#         if self.transform is not None:
#             try:
#                 sample = self.transform(sample)
#             except Exception as err:
#                 print('Error Occured: %s' % err, path)
#         if self.target_transform is not None:
#             target = self.target_transform(target)
#         return sample, ft_sample, target


# def generate_FT(image):
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     f = np.fft.fft2(image)
#     fshift = np.fft.fftshift(f)
#     fimg = np.log(np.abs(fshift)+1)
#     maxx = -1
#     minn = 100000
#     for i in range(len(fimg)):
#         if maxx < max(fimg[i]):
#             maxx = max(fimg[i])
#         if minn > min(fimg[i]):
#             minn = min(fimg[i])
#     fimg = (fimg - minn+1) / (maxx - minn+1)
#     return fimg

import cv2
import torch
import numpy as np
from torchvision import datasets


def opencv_loader(path):
    """
    Loads an image from the specified path using OpenCV.
    """
    img = cv2.imread(path)
    return img


def generate_FT(image):
    """
    Generates a normalized frequency domain representation (Fourier Transform)
    of a grayscale image.
    
    Args:
        image (numpy.ndarray): Input BGR image.

    Returns:
        numpy.ndarray: Normalized log-magnitude spectrum image.
    """
    # Convert image to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Compute 2D Fourier Transform
    f = np.fft.fft2(image)

    # Shift the zero frequency component to the center
    fshift = np.fft.fftshift(f)

    # Compute log magnitude spectrum
    fimg = np.log(np.abs(fshift) + 1)

    # Normalize the spectrum
    max_val = np.max(fimg)
    min_val = np.min(fimg)
    fimg = (fimg - min_val + 1) / (max_val - min_val + 1)

    return fimg


class DatasetFolderFT(datasets.ImageFolder):
    """
    Custom dataset class that extends torchvision.datasets.ImageFolder.
    It loads both the original image and its Fourier Transform (FT) representation.

    Args:
        root (str): Root directory path.
        transform (callable, optional): Optional transform to be applied on the input image.
        target_transform (callable, optional): Optional transform to be applied on the target.
        ft_width (int): Width to resize FT image.
        ft_height (int): Height to resize FT image.
        loader (callable): Function to load an image (default: OpenCV loader).
    """
    def __init__(self, root, transform=None, target_transform=None,
                 ft_width=10, ft_height=10, loader=opencv_loader):
        super(DatasetFolderFT, self).__init__(root, transform=transform,
                                              target_transform=target_transform,
                                              loader=loader)
        self.root = root
        self.ft_width = ft_width
        self.ft_height = ft_height

    def __getitem__(self, index):
        """
        Loads and returns a sample, its FT image, and the target class.

        Returns:
            tuple: (original image, FT image tensor, target label)
        """
        path, target = self.samples[index]

        # Load image
        sample = self.loader(path)

        # Generate FT image
        ft_sample = generate_FT(sample) if sample is not None else None

        # Error checking
        if sample is None:
            print(f"[Error] Original image is None --> {path}")
        if ft_sample is None:
            print(f"[Error] FT image is None --> {path}")

        assert sample is not None, f"Failed to load image: {path}"

        # Resize FT image and convert to tensor
        ft_sample = cv2.resize(ft_sample, (self.ft_width, self.ft_height))
        ft_sample = torch.from_numpy(ft_sample).float().unsqueeze(0)  # Add channel dim

        # Apply transforms if provided
        if self.transform is not None:
            try:
                sample = self.transform(sample)
            except Exception as err:
                print(f"[Transform Error] {err} --> {path}")

        if self.target_transform is not None:
            target = self.target_transform(target)

        return sample, ft_sample, target
