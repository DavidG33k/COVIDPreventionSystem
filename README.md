# COVIDPreventionSystem
Computer vision applied to COVID prevention techniques, developed for the thesis work by Davide Gena of the University of Calabria 2020/2021.

## Main library used
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/OpenCV_Logo_with_text_svg_version.svg/1200px-OpenCV_Logo_with_text_svg_version.svg.png" width="130" height="140">
The OpenCV library allows to recognize people in the video source by model of different neural deep network frameworks.

<br/>

In this case it was used the
[Mobilenet-SSD](https://docs.openvinotoolkit.org/2021.2/omz_models_public_mobilenet_ssd_mobilenet_ssd.html)
model of the Caffe framework.

<br/>
<br/>
<br/>

## OpenVINO Toolkit

<img src="https://opencv.org/wp-content/uploads/2018/10/openvino.png" width="450" height="90">
The performance can be increased with OpenVINO, a free toolkit developed by Intel to speed up the work of the neural network. To use it on this project you need to download and install the OpenVINO engine on your machine and uncomment two line of code in the "PreventionDetectors" class.

<br/>

Go
[Here](https://software.intel.com/content/www/us/en/develop/tools/openvino-toolkit/download.html)
to download the toolkit.

<br/>

To run it open in the same terminal the toolkit and after run the executable or your IDE, like PyCharm. To run the toolkit:

```bash
source /opt/intel/openvino_2021/bin/setupvars.sh
```

to run your IDE (PyCharm in this case):

```bash
cd pycharm-XXXX.X/bin/
./pycharm.sh
```

<br/>

## Interface
<img src="https://raw.githubusercontent.com/PySimpleGUI/PySimpleGUI/master/images/for_readme/Logo%20with%20text%20for%20GitHub%20Top.png" width="350" height="150">
The interface, that allow to configure the system, was developed with the PySimpleGUI library. This library simplifies many others graphics framework and work by default with Tkinter.

<br/>
<br/>

Here are some examples of the interface and system operation.

<br/>

Main interface:

<img src="https://github.com/DavidG33k/COVIDPreventionSystem/blob/main/examples/interface-example.png">

<br/>

Examples of gathering detection:

<img src="https://github.com/DavidG33k/COVIDPreventionSystem/blob/main/examples/detection_clip2.png">
<img src="https://github.com/DavidG33k/COVIDPreventionSystem/blob/main/examples/detection_clip3.png">

<br/>

Example of mvement detection:

<img src="https://github.com/DavidG33k/COVIDPreventionSystem/blob/main/examples/movement-detector-example.png">

<br/>

A portion of log file:

<img src="https://github.com/DavidG33k/COVIDPreventionSystem/blob/main/examples/log-example.png">
