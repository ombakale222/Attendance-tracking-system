

# from torch.utils.data import DataLoader
# from src.data_io.dataset_folder import DatasetFolderFT
# from src.data_io import transform as trans


# def get_train_loader(conf):
#     train_transform = trans.Compose([
#         trans.ToPILImage(),
#         trans.RandomResizedCrop(size=tuple(conf.input_size),
#                                 scale=(0.9, 1.1)),
#         trans.ColorJitter(brightness=0.4,
#                           contrast=0.4, saturation=0.4, hue=0.1),
#         trans.RandomRotation(10),
#         trans.RandomHorizontalFlip(),
#         trans.ToTensor()
#     ])
#     root_path = '{}/{}'.format(conf.train_root_path, conf.patch_info)
#     trainset = DatasetFolderFT(root_path, train_transform,
#                                None, conf.ft_width, conf.ft_height)
#     train_loader = DataLoader(
#         trainset,
#         batch_size=conf.batch_size,
#         shuffle=True,
#         pin_memory=True,
#         num_workers=16)
#     return train_loader
from torch.utils.data import DataLoader
from src.data_io.dataset_folder import DatasetFolderFT
from src.data_io import transform as trans


def get_train_loader(conf):
    """
    Creates and returns a DataLoader for the training dataset with data augmentation.

    Args:
        conf: A configuration object containing training parameters like:
              - input_size (tuple): Size to which images are cropped/resized.
              - train_root_path (str): Path to the root training directory.
              - patch_info (str): Sub-directory or patch set info.
              - batch_size (int): Number of samples per batch.
              - ft_width (int): Width for Fourier Transform image.
              - ft_height (int): Height for Fourier Transform image.

    Returns:
        torch.utils.data.DataLoader: DataLoader for the training set.
    """

    # Define image augmentation pipeline
    train_transform = trans.Compose([
        trans.ToPILImage(),
        trans.RandomResizedCrop(
            size=tuple(conf.input_size),
            scale=(0.9, 1.1)  # Random crop scale between 90%–110%
        ),
        trans.ColorJitter(
            brightness=0.4,
            contrast=0.4,
            saturation=0.4,
            hue=0.1
        ),
        trans.RandomRotation(10),         # Rotate image ±10 degrees
        trans.RandomHorizontalFlip(),     # Random left-right flip
        trans.ToTensor()
    ])

    # Construct full root path for training data
    root_path = f'{conf.train_root_path}/{conf.patch_info}'

    # Create training dataset using DatasetFolderFT
    trainset = DatasetFolderFT(
        root=root_path,
        transform=train_transform,
        target_transform=None,
        ft_width=conf.ft_width,
        ft_height=conf.ft_height
    )

    # Create DataLoader
    train_loader = DataLoader(
        trainset,
        batch_size=conf.batch_size,
        shuffle=True,          # Shuffle data at every epoch
        pin_memory=True,       # Speed up host to device transfer
        num_workers=16         # Number of parallel data loading workers
    )

    return train_loader
