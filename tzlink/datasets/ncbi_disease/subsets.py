#!/usr/bin/env python3
# coding: utf8

# Author: Lenz Furrer, 2018


'''
Filename listings for train/dev/test and different folds.
'''


import os
import operator


filenames = {
    'train': 'NCBItrainset_corpus.txt',
    'dev': 'NCBIdevelopset_corpus.txt',
    'test': 'NCBItestset_corpus.txt',
}


def prepare(dir_, subset):
    '''
    Iterate over pairs <path, document selector>.
    '''
    def _path(label):
        return os.path.join(dir_, filenames[label])

    # The first fold is the train/dev split provided by the corpus creators.
    if subset in ('test', 'dev', 'dev1', 'train', 'train1'):
        yield (_path(subset.rstrip('1')), iter)
        return

    # Use one of the alternative dev/train splits.
    n = int(subset.lstrip('traindev')) - 2  # "dev2" is the first alt-subset
    fold = set(_folds[n])
    if subset.startswith('train'):
        yield (_path('dev'), iter)
        check = operator.not_
    elif subset.startswith('dev'):
        check = bool
    else:
        raise ValueError('invalid subset: {}'.format(subset))
    def _select(docs):
        for i, doc in enumerate(docs):
            if check(i in fold):
                yield doc
    yield (_path('train'), _select)




_dev2 = [
    2, 3, 18, 19, 27, 32, 34, 55, 57, 64, 67, 68, 69, 82, 83, 93, 94, 95,
    100, 104, 105, 113, 118, 126, 130, 133, 139, 143, 145, 151, 157, 158,
    173, 176, 181, 185, 187, 198, 199, 204, 205, 211, 219, 242, 245, 276,
    281, 284, 289, 290, 293, 297, 305, 312, 324, 332, 335, 340, 347, 348,
    358, 362, 366, 371, 373, 375, 378, 385, 387, 404, 425, 431, 434, 437,
    441, 443, 444, 452, 463, 466, 473, 486, 488, 489, 490, 506, 515, 516,
    517, 524, 533, 537, 549, 550, 558, 562, 582, 583, 585]
_dev3 = [
    4, 8, 9, 11, 14, 20, 22, 28, 30, 33, 45, 49, 51, 56, 66, 71, 84, 91,
    115, 123, 125, 128, 129, 135, 136, 138, 140, 147, 156, 167, 174, 175,
    192, 208, 210, 213, 226, 238, 251, 256, 258, 267, 273, 275, 279, 282,
    291, 292, 296, 300, 303, 307, 313, 315, 326, 342, 346, 352, 355, 360,
    374, 377, 379, 383, 388, 398, 400, 401, 408, 409, 417, 429, 447, 449,
    453, 454, 459, 462, 468, 469, 487, 495, 502, 504, 511, 513, 514, 519,
    520, 525, 545, 554, 556, 559, 563, 578, 579, 581, 592]
_dev4 = [
    5, 7, 12, 13, 15, 37, 39, 42, 58, 63, 72, 73, 75, 81, 102, 106, 108,
    111, 114, 122, 127, 141, 149, 161, 163, 165, 172, 177, 184, 191, 195,
    197, 201, 207, 209, 212, 215, 218, 220, 223, 236, 241, 243, 246, 247,
    249, 262, 266, 278, 280, 283, 301, 302, 310, 314, 316, 320, 325, 328,
    329, 330, 349, 356, 359, 363, 369, 384, 395, 397, 410, 414, 415, 421,
    424, 426, 428, 432, 442, 445, 450, 455, 458, 460, 464, 470, 476, 482,
    492, 498, 507, 523, 526, 541, 546, 547, 553, 571, 574, 586]
_dev5 = [
    0, 16, 17, 21, 31, 36, 50, 59, 60, 61, 70, 77, 78, 79, 80, 96, 101,
    103, 112, 116, 124, 134, 142, 144, 146, 152, 153, 166, 170, 171, 178,
    186, 194, 200, 202, 203, 214, 217, 222, 228, 230, 232, 237, 239, 254,
    259, 261, 263, 264, 285, 286, 287, 288, 298, 318, 319, 321, 331, 334,
    336, 339, 345, 350, 367, 376, 381, 389, 390, 393, 394, 411, 412, 420,
    430, 436, 439, 446, 451, 467, 472, 477, 479, 483, 491, 493, 494, 501,
    503, 508, 527, 555, 557, 560, 568, 575, 576, 580, 584, 591]
_dev6 = [
    1, 29, 35, 40, 48, 54, 65, 76, 88, 89, 90, 92, 99, 109, 119, 121, 131,
    137, 148, 154, 159, 160, 164, 168, 179, 180, 182, 193, 196, 206, 221,
    225, 227, 229, 231, 233, 244, 248, 250, 257, 260, 265, 269, 270, 271,
    277, 295, 304, 309, 317, 323, 333, 337, 338, 353, 354, 361, 368, 372,
    382, 386, 396, 399, 403, 405, 413, 422, 427, 433, 435, 438, 448, 456,
    465, 471, 474, 480, 481, 485, 496, 497, 499, 500, 505, 522, 529, 539,
    540, 542, 543, 548, 551, 552, 564, 566, 572, 573, 587, 590]
_dev7 = [
    6, 10, 23, 24, 25, 26, 38, 41, 43, 44, 46, 47, 52, 53, 62, 74, 85, 86,
    87, 97, 98, 107, 110, 117, 120, 132, 150, 155, 162, 169, 183, 188, 189,
    190, 216, 224, 234, 235, 240, 252, 253, 255, 268, 272, 274, 294, 299,
    306, 308, 311, 322, 327, 341, 343, 344, 351, 357, 364, 365, 370, 380,
    391, 392, 402, 406, 407, 416, 418, 419, 423, 440, 457, 461, 475, 478,
    484, 509, 510, 512, 518, 521, 528, 530, 531, 532, 534, 535, 536, 538,
    544, 561, 565, 567, 569, 570, 577, 588, 589]


_folds = [_dev2, _dev3, _dev4, _dev5, _dev6, _dev7]
