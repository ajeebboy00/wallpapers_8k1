import 'package:flutter/material.dart';

class ExploreScreen extends StatelessWidget {
  const ExploreScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Explore Wallpapers', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: const Center(
        child: Text('Explore Wallpapers Grid', style: TextStyle(color: Colors.grey)),
      ),
    );
  }
}
