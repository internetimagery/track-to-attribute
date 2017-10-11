# Take tracker data from nuke to maya attributes

    import track2attr
    track2attr.main()
    
* Open a nuke file.
* Select one of the trackers in the drop down.
* Select an attribute in the channelbox (maya) and press one of the "<< CB" buttons.
* Click "Keyframe" to set your keys.
* Open the graph editor, bringing the attributes animation curve into focus.
* Scrub to an extreme on the curve.
* Move the entire curve up and down (in graph editor) till the desired position in the viewport is attained.
* Enable the region scale tool.
* Scrub to the opposing extreme on the curve.
* Scale the curve (from the extreme side) till the desired position in the viewport is also attained.
* All the keys between the extremes should work just fine.

A good rule of thumb is to track as many points as you can. Then use the stabalize field to pick the body part next down the chain. ie: tracking a nose for head rotation data would stabalize to the chest/neck. Tracking the chest would stabalize to the hips. Hips to the environment (still object tracks camera shake).

####Why?

This is useful as a poor-mans motion capture. A quick way to get data out of video footage and into your scene. A niche tool for sure. But certainly useful every now and again.
