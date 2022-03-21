//wrap the file with the version
#local Temp_version = version;
#version 3.7;

 
global_settings {
  //This setting is for alpha transparency to work properly.
  //Increase by a small amount if transparent areas appear dark.
   max_trace_level 15
   adc_bailout 0.01
   assumed_gamma 1
   ambient_light rgb <1,1,1>*100
 
}
#include "detail0_POV_geom_.inc" 
#include "detail1_POV_geom_.inc" 
#include "detail2_POV_geom_.inc" 

#include "metal_custom.inc"
#include "colors.inc"
#include "metals.inc"
#include "transforms.inc"
 
//CAMERA PoseRayCAMERA
//CAMERA PoseRayCAMERA
camera {
        perspective
        right -x*image_width/image_height
        location <0,0,1414>
        look_at 0
        rotate <0,0,0>
        rotate <0,5,0>
        rotate <0,0,0>

        }

 
//PoseRay default Light attached to the camera
light_source {
              <0,0,700> //light position
              color rgb <1,1,1>*1.7
              rotate <0,0,0> //roll
              rotate <0,0 ,0> //pitch
              rotate <0,0,0> //yaw
             }


//background lighting
light_source {
              <0,0,2000> //light position
              color rgb <0.4,0.4,0.3>
              rotate <75,0,0> //roll
              rotate <0,0,0> //pitch
              rotate <0,0,0> //yaw
             }

light_source {
              <0,0,2000> //light position
              color rgb <0.4,0.4,0.3>
              rotate <-75,0,0> //roll
              rotate <0,0,0> //pitch
              rotate <0,0,0> //yaw
             }


light_source {
              <0,0,2000> //light position
              color rgb <0.4,0.4,0.3>
              rotate <0,0,0> //roll
              rotate <0,75,0> //pitch
              rotate <0,0,0> //yaw
             }

light_source {
              <0,0,2000> //light position
              color rgb <0.4,0.4,0.3>
              rotate <0,0,0> //roll
              rotate <0,-75,0> //pitch
              rotate <0,0,0> //yaw
             }


//Background
background { color srgbt <0,0,0,1>  }

object{
      detail1


//            rotate <,0,0> //roll
//	    rotate <0,,0> //pitch
//    	    rotate <0,0,> //yaw
	    Matrix_Trans(<-0.7961310308341965,-0.5493621212860933,0.253725523822345,0.0>, <0.6039055203370572,-0.6947138315421155,0.3907311284892737,0.0>, <-0.038386250784724935,0.46429942058990004,0.8848460565491465,0.0>, <0.0,0.0,0.0,1.0>)

            translate <-82,-51,-63>


      texture { pigment { color rgb <0.64,0.687,0.71>  }

	        finish{F_MetalD}
                normal  { agate 0.1 scale 0.1 }}

      }
