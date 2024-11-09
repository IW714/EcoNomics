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
                zIndex: -1, // Render behind other content
            }}
        >
        <ShaderGradient
            control='query'
            urlString='https://www.shadergradient.co/customize?animate=on&axesHelper=on&bgColor1=%23000000&bgColor2=%23000000&brightness=1.2&cAzimuthAngle=60&cDistance=7.1&cPolarAngle=90&cameraZoom=19&color1=%23ffbf69&color2=%23cbf3f0&color3=%232ec4b6&destination=onCanvas&embedMode=off&envPreset=dawn&format=gif&fov=45&frameRate=10&grain=off&http%3A%2F%2Flocalhost%3A3002%2Fcustomize%3Fanimate=on&lightType=3d&pixelDensity=1&positionX=0&positionY=-0.15&positionZ=0&range=enabled&rangeEnd=40&rangeStart=0&reflection=0.1&rotationX=0&rotationY=0&rotationZ=0&shader=defaults&type=sphere&uAmplitude=4&uDensity=4&uFrequency=5.5&uSpeed=0.1&uStrength=2&uTime=0&wireframe=false&zoomOut=true'/>
        </ShaderGradientCanvas>
    )
}

export default Gradient;