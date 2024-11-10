import { ShaderGradientCanvas, ShaderGradient } from '@shadergradient/react';

function Gradient() {
    return (
        <ShaderGradientCanvas
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                zIndex: 1,
                opacity: 0.8  // Added opacity to let the background show through
            }}
        >
        <ShaderGradient
            control='query'
            urlString='https://www.shadergradient.co/customize?animate=on&axesHelper=on&bgColor1=%23000000&bgColor2=%23000000&brightness=1.8&cAzimuthAngle=0&cDistance=7.1&cPolarAngle=140&cameraZoom=7.6&color1=%23000000&color2=%230458DE&color3=%230AC457&destination=onCanvas&embedMode=off&envPreset=dawn&format=gif&fov=45&frameRate=10&grain=off&lightType=3d&pixelDensity=1&positionX=-1&positionY=-0.8&positionZ=0&range=enabled&rangeEnd=40&rangeStart=0&reflection=0.1&rotationX=0&rotationY=0&rotationZ=0&shader=defaults&type=sphere&uAmplitude=0.5&uDensity=8.5&uFrequency=5.5&uSpeed=.1&uStrength=0.2&uTime=0&wireframe=false'/>
        </ShaderGradientCanvas>
    )
}

export default Gradient;