from inc_noesis import *
from inc_xbox360_untile import *
import math

def registerNoesisTypes():
    handle = noesis.register("X360 texture SWIZZ", ".Texture2D")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
    return 1

def noepyCheckType(data):
    return 1

def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    dataOffset = 0x14d       #set the data offset
    datasize = bs.getSize() - dataOffset
    imgFmt = 3               #set image format (1 - 7)
    imgWidth = 512          #set image width
    imgHeight = 1024          #set image height
    bs.seek(dataOffset, NOESEEK_ABS)
    data = bs.readBytes(datasize)
    #DXT1
    if imgFmt == 1:
        data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 8)
        texFmt = noesis.NOESISTEX_DXT1
    #DXT3
    elif imgFmt == 2:
        data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 16)
        texFmt = noesis.NOESISTEX_DXT3
    #DXT5
    elif imgFmt == 3:
        data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 16)
        texFmt = noesis.NOESISTEX_DXT5
    #DXT5 packed normal map
    elif imgFmt == 4:
        data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 16)
        data = rapi.imageDecodeDXT(data, imgWidth, imgHeight, noesis.FOURCC_ATI2)
        texFmt = noesis.NOESISTEX_RGBA32
    #DXT5 packed normal map2
    elif imgFmt == 5:
        data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 16)
        data = rapi.imageDecodeDXT(data, imgWidth, imgHeight, noesis.FOURCC_ATI1)
        texFmt = noesis.NOESISTEX_RGBA32
    #DXT1 packed normal map
    elif imgFmt == 6:
        data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 8)
        data = rapi.imageDecodeDXT(data, imgWidth, imgHeight, noesis.FOURCC_DXT1NORMAL)
        texFmt = noesis.NOESISTEX_RGBA32
    #raw
    elif imgFmt == 7:
        data = rapi.imageUntile360Raw(data, imgWidth, imgHeight, 4)
        data = rapi.imageDecodeRaw(data, imgWidth, imgHeight, "a8r8g8b8")
        texFmt = noesis.NOESISTEX_RGBA32
    #unknown, not handled
    else:
        print("WARNING: Unhandled image format")
        return None
    texList.append(NoeTexture(rapi.getInputName(), imgWidth, imgHeight, data, texFmt))
    return 1
    
def texWriteRGBA(data, width, height, bs):
    DXT5Data = rapi.imageEncodeDXT(data,4,width,height,noesis.NOE_ENCODEDXT_BC3)
    DXT5Data = rapi.swapEndianArray(DXT5Data, 2)
    outData = XGTileSurfaceFromLinearTexture(DXT5Data,width, height,"DXT5") 
    bs.writeBytes(outData)
    return 1
    
widthList = (2,4,8,16,32,64,128,256,512,1024,2048) 

def getWidthHeight(buffSize):
    tWidth = int(math.sqrt(buffSize * 2))
    if tWidth not in widthList:
        sizeList = []
        for i in range(len(widthList)):
            index = len(widthList) - 1 - i
            tWidth = widthList[index]
            for j in range(len(widthList)):
                tHeight = widthList[j]
                size = tWidth * tHeight // 2
                sizeList.append((size,tWidth,tHeight))
        for i in range(len(sizeList)):
            info = sizeList[i]
            if info[0] == buffSize:
                width = info[1] 
                height = info[2]
                if (width // height) == 2 or (height // width) == 2:
                    return (info[1],info[2])
            
    
    return (tWidth,tWidth) 